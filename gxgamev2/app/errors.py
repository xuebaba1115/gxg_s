# coding:utf8

#1000~2000
#2000+ 

_error={
1:"room is full",
2:"play get card error",
3:'error_fapai',
2000:"liuju"
}


def getError(errorid):
    err=_error.get(errorid)
    return err