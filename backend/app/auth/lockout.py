from datetime import datetime,timedelta,timezone
DURATIONS=(60,300,900,3600)
def failure_state(failed_count:int,level:int,now:datetime|None=None):
    count=failed_count+1
    if count<5:return count,level,None
    new_level=min(4,level+1);instant=now or datetime.now(timezone.utc);return 0,new_level,instant+timedelta(seconds=DURATIONS[new_level-1])
