# -*- coding:utf-8 -*-
# @Time     : 2020/1/13 11:46
# @Author   : zhouliang02
# @description  :
import copy
import os
import time

left, down, stay = (0, 1), (1, 0), (1, 1)


class Path(object):
    def __init__(self, end, path, count=0):
        self.end = end
        self.path = path
        # print path
        self.count = count

    def create_new_path(self, end, new_p, count):
        c = self.path[:]  # copy.deepcopy(self.path)
        c.append(new_p)
        return Path(end, c, count)

    def print_path(self):
        str_map = {left: "+", down: "-", stay: "stay"}
        for item in self.path:
            print(str_map[item])


class TextType(object):
    def __init__(self):
        pass

    def transform_add(self, line):
        return "{}{}".format(line, os.linesep)

    def transform_delete(self, line):
        return "{}{}".format(line, os.linesep)

    def no_change(self, line):
        return "{}{}".format(line, os.linesep)


class HTMLTextType(TextType):
    def __init__(self):
        super(HTMLTextType, self).__init__()

    def transform_add(self, line):
        return "<span style=\"background:green;\">{}</span><br/>{}".format(line, os.linesep)

    def transform_delete(self, line):
        return "<span style=\"background:red;\">{}</span><br/>{}".format(line, os.linesep)

    def no_change(self, line):
        return "<span>{}</span><br/>{}".format(line, os.linesep)


class TerminalTextType(TextType):
    def __init__(self):
        super(TerminalTextType, self).__init__()

    def transform_add(self, line):
        return "\033[0;32;m{}\033[0m{}".format(line, os.linesep)

    def transform_delete(self, line):
        return "\033[0;31;m{}\033[0m{}".format(line, os.linesep)

    def no_change(self, line):
        return "{}{}".format(line, os.linesep)


class Diff(object):
    # add, delete, no_change
    left, down, stay = (0, 1), (1, 0), (1, 1)

    def __init__(self):
        self.pre_file_path = None
        self.after_file_path = None
        self.pre_str_list = None
        self.after_str_list = None
        self.change_path = None

    def _init_dp(self):
        dp = [[len(self.pre_str_list) + len(self.after_str_list) + 1] * (len(self.after_str_list) + 1) for i in
              range(len(self.pre_str_list) + 1)]
        dp[0][0] = 0
        path_dp = {(0, 0): Path((0, 0), [], 0)}
        for i in range(1, len(self.after_str_list) + 1):
            dp[0][i] = dp[0][i - 1] + 1
            path_dp[(0, i)] = path_dp.get((0, i - 1)).create_new_path((0, i), left, dp[0][i])
        for i in range(1, len(self.pre_str_list) + 1):
            dp[i][0] = dp[i - 1][0] + 1
            path_dp[(i, 0)] = path_dp.get((i - 1, 0)).create_new_path((i, 0), down, dp[0][i])

        return dp, path_dp

    def _find_min_path(self, dp, path_dp):
        times = 0
        all_time = 0

        # dp 开始
        for i in range(1, len(dp)):
            for j in range(1, len(dp[i])):
                times += 1
                # default stay
                begin_time = time.time()
                if self.pre_str_list[i - 1] == self.after_str_list[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                if dp[i - 1][j] < dp[i][j - 1]:
                    # down  pk stay
                    if dp[i - 1][j] + 1 < dp[i][j]:
                        # down
                        dp[i][j] = dp[i - 1][j] + 1
                        path_dp[(i, j)] = path_dp[(i - 1, j)].create_new_path((i, j), down, dp[i][j])
                    else:
                        # stay
                        path_dp[(i, j)] = path_dp[(i - 1, j - 1)].create_new_path((i, j), stay, dp[i][j])
                else:
                    # left pk stay
                    if dp[i][j - 1] + 1 < dp[i][j]:
                        # left
                        dp[i][j] = dp[i][j - 1] + 1
                        path_dp[(i, j)] = path_dp[(i, j - 1)].create_new_path((i, j), left, dp[i][j])
                    else:
                        # stay
                        path_dp[(i, j)] = path_dp[(i - 1, j - 1)].create_new_path((i, j), stay, dp[i][j])
                all_time += time.time() - begin_time
        print("dp is close {}".format(all_time))
        print("avg time is {}".format(all_time/times))

        return path_dp[(len(dp) - 1, len(dp[0]) - 1)]

    def _find_min_path_version1(self):
        # 优化空间复杂度

        pass

    def compare_file(self, pre_file_path, after_file_path):
        if not os.path.exists(pre_file_path) or not os.path.exists(pre_file_path):
            return False
        self.after_file_path = after_file_path
        self.pre_file_path = pre_file_path
        with open(self.pre_file_path, "rU") as pre_file:
            self.pre_str_list = pre_file.read().split("\n")
        with open(self.after_file_path, "rU") as after_file:
            self.after_str_list = after_file.read().split("\n")

        dp, path_dp = self._init_dp()
        self.change_path = self._find_min_path(dp, path_dp)
        return True

    def out_change_file(self, out_file, txt_type=TextType()):
        pre_index = after_index = 0
        str_text = ""
        for d in self.change_path.path:
            if d == left:
                str_text += txt_type.transform_add("+ {}".format(self.after_str_list[after_index]))
                after_index += 1
            elif d == down:
                str_text += txt_type.transform_delete("- {}".format(self.pre_str_list[pre_index]))
                pre_index += 1
            else:
                str_text += txt_type.no_change(
                    "{}".format(self.after_str_list[after_index], self.pre_str_list[pre_index]))
                after_index += 1
                pre_index += 1
        with open(out_file, "w") as op_file:
            op_file.write(str_text)

    def get_step_count(self):
        return self.change_path.count
