import time


class RateLimiter:
    def __init__(self, algorithm):
        self.algorithm =algorithm

    def allow(self, user_id):
        return self.algorithm.allow(user_id)


class FixedWindow:
    def __init__(self, max_requests=100, window_size=60):
        self.max_requests=max_requests
        self.window_size=window_size
        self.users={}

    def allow(self,user_id):
        now=time.time()
        if user_id not in self.users:
            self.users[user_id]={
                "requests_pending":self.max_requests-1,
                "window_start":now
                }
            return True

        else:
            user=self.users[user_id]
            requests_pending=user["requests_pending"]
            window_start= user["window_start"]
            time_elapsed= now-window_start

            if time_elapsed>=self.window_size:
                user["requests_pending"]=self.max_requests-1
                user["window_start"] =now
                return True

            if requests_pending>0:
                user["requests_pending"]-=1
                return True

            return False

class TokenBucket:
    def __init__(self, max_tokens=100,refill_rate=1):
        self.max_tokens=max_tokens
        self.refill_rate=refill_rate
        self.users={}

    def allow(self, user):
        if user not in self.users:
            self.users[user]={
                "tokens":self.max_tokens-1,
                "last_refill":time.time()
            }
            return True
        else:
            user=self.users[user]
            tokens=user["tokens"]
            last_refill=user["last_refill"]
            time_elapsed=time.time()-last_refill

            user["tokens"]=min(self.max_tokens,tokens+self.refill_rate*time_elapsed)
            user["last_refill"]=time.time()


            if user["tokens"]>0:
                user["tokens"]-=1
                return True

            return False

class SlidingWindow:
    def __init__(self, max_requests=100, window_size=60):
        self.max_requests=max_requests
        self.window_size=window_size
        self.users={}

    def allow(self,user_id):
        now=time.time()
        if user_id not in self.users:
            self.users[user_id]=[now]
            return True
        else:
            request_times=self.users[user_id]
            request_times=[timestamp for timestamp in request_times if now-timestamp<self.window_size]
            if len(request_times)<self.max_requests:
                request_times.append(now)
                self.users[user_id]=request_times
                return True
            return False
