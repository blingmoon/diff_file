# -*- coding:utf-8 -*-
# @Time     : 2020/1/14 16:33
# @Author   : zhouliang02
# @description  :
import time

from diff_file.diff import Diff, HTMLTextType

if __name__ == "__main__":
    pre_file_path = "../test_file/test_before"
    after_file_path = "../test_file/test_after"
    out_file_path = "../test_file/compare.html"
    diff = Diff()
    start_time = time.time()
    if diff.compare_file(pre_file_path, after_file_path):
        diff.out_change_file(out_file_path, HTMLTextType())
    else:
        print("compare_file failed")
    after_time = time.time()
    print("time is {}".format(after_time-start_time))
    print("change count is {}".format(diff.get_step_count()))
