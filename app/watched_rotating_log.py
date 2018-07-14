#coding=utf8

from __future__ import with_statement

import os
import sys
import time
import errno
import logging
from logging.handlers import BaseRotatingHandler
from stat import ST_DEV, ST_INO

try:
    import codecs
except ImportError:
    codecs = None

class FileLock(object):
    '''
    A file locking mechanism that has context-manager support so 
    you can use it in a ``with`` statement. This should be relatively cross
    compatible as it doesn't rely on ``msvcrt`` or ``fcntl`` for the locking.
    '''
 
    class FileLockException(Exception):
        pass
 
    def __init__(self, protected_file_path, timeout=1, delay=0.1, lock_file_contents=''):
        '''
        Prepare the file locker. Specify the file to lock and optionally
        the maximum timeout and the delay between each attempt to lock.
        '''
        self.lockfile = protected_file_path + '.lock'
        self.timeout = timeout
        self.delay = delay
        self.lock_file_contents = lock_file_contents

        self.is_locked = False
 
    def acquire(self, blocking=True):
        ''' 
        Acquire the lock, if possible. 
        If the lock is in use, and `blocking` is False, return False.
        Otherwise, check again every `self.delay` seconds until it either gets 
        the lock or exceeds `timeout` number of seconds, in which case it 
        raises an timeout exception.
        '''
        start_time = time.time()
        while True:
            try:
                # Attempt to create the lockfile.
                # These flags cause os.open to raise an OSError if the file already exists.
                fd = os.open( self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR )
                break
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise 
                if (time.time() - start_time) >= self.timeout:
                    raise FileLock.FileLockException('Timeout occurred.')
                if not blocking:
                    return False
                time.sleep(self.delay)
        self.is_locked = True
        return True
 
    def release(self):
        ''' 
        Get rid of the lock by deleting the lockfile. 
        When working in a `with` statement, this gets automatically 
        called at the end.
        '''
        if self.is_locked:
            self.is_locked = False
            os.unlink(self.lockfile)
 
    def __enter__(self):
        ''' 
        Activated when used in the with statement. 
        Should automatically acquire a lock to be used in the with block.
        Timeout means the lock is dummy, so it will remove dummy lock and 
        acquire the lock anyway.
        This is not a strict lock, just try best to keep synced.
        '''
        try:
            self.acquire()
        except FileLock.FileLockException:
            os.unlink(self.lockfile)
            self.acquire()
        return self
 
    def __exit__(self, type, value, traceback):
        ''' 
        Activated at the end of the with statement.
        It automatically releases the lock if it isn't locked.
        '''
        if self.is_locked:
            self.release()
 
    def __del__(self):
        ''' 
        Make sure this ``FileLock`` instance doesn't leave a .lock file
        lying around.
        '''
        if self.is_locked:
            self.release()


class WatchedRotatingFileHandler(logging.FileHandler):
    '''
    Combination of RotatingFileHandler and WatchedFileHandler.
    '''

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None):
        # RotatingFileHandler
        if maxBytes > 0:
            mode = 'a' # doesn't make sense otherwise!

        if codecs is None:
            encoding = None
        logging.FileHandler.__init__(self, filename, mode, encoding)
        self.mode = mode
        self.encoding = encoding
        self.maxBytes = maxBytes
        self.backupCount = backupCount

        # WatchedFileHandler
        if not os.path.exists(self.baseFilename):
            self.dev, self.ino = -1, -1
        else:
            stat = os.stat(self.baseFilename)
            self.dev, self.ino = stat[ST_DEV], stat[ST_INO]

    def check_stat(self):   
        '''
        Check if log file changed.
        '''         
        stat = None
        changed = 1

        if os.path.exists(self.baseFilename):
            try:
                stat = os.stat(self.baseFilename)
                changed = (stat[ST_DEV] != self.dev) or (stat[ST_INO] != self.ino)
            except OSError:
                pass
        return stat, changed

    def emit(self, record):
        '''
        Emit a record.

        First check if the underlying file has changed, and if it
        has, close the old stream and reopen the file to get the
        current stream.

        Output the record to the file, catering for rollover as described
        in doRollover().
        '''
        # WatchedFileHandler
        stat, changed = self.check_stat()

        if changed and self.stream is not None:
            try:
                self.stream.flush()
                self.stream.close()
                self.stream = open(self.baseFilename, 'w')
                if stat is None:
                    try:
                        stat = os.stat(self.baseFilename)
                    except OSError:
                        return
                self.dev, self.ino = stat[ST_DEV], stat[ST_INO]
            except ValueError:
                pass

        # RotatingFileHandler
        try:
            if self.shouldRollover(record):
                with FileLock(self.baseFilename, timeout=1, delay=0.1, lock_file_contents=os.getpid()):
                    # check again and do rollover if necessary
                    if self.shouldRollover(record):
                        self.doRollover()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def doRollover(self):
        '''
        Do a rollover.
        '''
        stat, changed = self.check_stat()
        if changed:
            return

        try:
            self.stream.close()
            if self.backupCount > 0:
                for i in range(self.backupCount - 1, 0, -1):
                    sfn = '%s.%d' % (self.baseFilename, i)
                    dfn = '%s.%d' % (self.baseFilename, i + 1)
                    if os.path.exists(sfn):
                        if os.path.exists(dfn):
                            os.remove(dfn)
                        os.rename(sfn, dfn)
                dfn = self.baseFilename + '.1'
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(self.baseFilename, dfn)
            if self.encoding:
                self.stream = codecs.open(self.baseFilename, 'w', self.encoding)
            else:
                self.stream = open(self.baseFilename, 'w')
        except:
            return

    def shouldRollover(self, record):
        '''
        Determine if rollover should occur.

        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.
        '''
        if self.maxBytes > 0:                   # are we rolling over?
            msg = '%s\n' % self.format(record)
            try:
                self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
                if self.stream.tell() + len(msg) >= self.maxBytes:
                    return 1
            except:
                return 0
        return 0


