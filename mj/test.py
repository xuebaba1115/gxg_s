#-*-coding:ascii-*-
import split
from multiprocessing import Pool
import os,time


def run_proc(cards):
    if split.get_hu_info(cards, 34, 33):
        pass
    else:
        pass
        # print "can't"

def main():
    # cards = [1, 1, 1, 0, 0, 0, 1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 0, 0, 0, 0, 0, 0, 2]
    cards = [0, 0, 1, 0, 2, 2, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0]
    count=0
    start = time.time()
    p = Pool(4)
    while time.time()-start<20:
        p.apply_async(run_proc, args=(cards,))
        count+=1
    p.close()  
    p.join()
    print count
          
        # count+=1 
        # if split.get_hu_info(cards, 34, 33):
        #     pass
        # else:
        #     pass
        # print count            

if __name__ == "__main__":
    main()
