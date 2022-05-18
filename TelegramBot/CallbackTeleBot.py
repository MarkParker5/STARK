from telebot import TeleBot, util, apihelper


# added callback for __threaded_polling
class CallbackTeleBot(TeleBot):
    def polling(self, none_stop=False, interval=0, timeout=20, callback = lambda *args: None, args = () ):
        if self.threaded:
            self.__threaded_polling(none_stop, interval, timeout, callback, args)
        else:
            self._TeleBot__non_threaded_polling(none_stop, interval, timeout)

    def __threaded_polling(self, none_stop=False, interval=0, timeout=20, callback = lambda *args: None, args = () ):
        self._TeleBot__stop_polling.clear()
        error_interval = 0.25

        polling_thread = util.WorkerThread(name="PollingThread")
        or_event = util.OrEvent(
            polling_thread.done_event,
            polling_thread.exception_event,
            self.worker_pool.exception_event
        )

        while not self._TeleBot__stop_polling.wait(interval):
            callback(*args)      #   added by Parker
            or_event.clear()
            try:
                polling_thread.put(self._TeleBot__retrieve_updates, timeout)

                or_event.wait()  # wait for polling thread finish, polling thread error or thread pool error

                polling_thread.raise_exceptions()
                self.worker_pool.raise_exceptions()

                error_interval = 0.25
            except apihelper.ApiException as e:
                if not none_stop:
                    self._TeleBot__stop_polling.set()
                else:
                    polling_thread.clear_exceptions()
                    self.worker_pool.clear_exceptions()
                    time.sleep(error_interval)
                    error_interval *= 2
            except KeyboardInterrupt:
                self._TeleBot__stop_polling.set()
                break

        polling_thread.stop()
