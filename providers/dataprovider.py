#!/usr/bin/python3

import libsysrepoPython3 as sr
import sys


class DataProvider:

    def __init__(self, module_name):
        self.module_name = module_name
        self.connect()

    def connect(self):
        self.conn = sr.Connection("provider_%s" % (self.module_name))
        self.session = sr.Session(self.conn)
        self.subscribe = sr.Subscribe(self.session)

        self.subscribe.module_change_subscribe(self.module_name, self.callback)

        sr.global_loop()

    def print_change(self, op, old_val, new_val):
        if (op == sr.SR_OP_CREATED):
            print("CREATED: ", end='')
            print(new_val.to_string(), end='')
        elif (op == sr.SR_OP_DELETED):
            print("DELETED: ", end='')
            print(old_val.to_string(), end='')
        elif (op == sr.SR_OP_MODIFIED):
            print("MODIFIED: ", end='')
            print("old value", end='')
            print(old_val.to_string(), end='')
            print("new value", end='')
            print(new_val.to_string(), end='')
        elif (op == sr.SR_OP_MOVED):
            print("MOVED: " + new_val.xpath() + " after " + old_val.xpath())

    def ev_to_str(self, ev):
        if (ev == sr.SR_EV_VERIFY):
            return "verify"
        elif (ev == sr.SR_EV_APPLY):
            return "apply"
        elif (ev == sr.SR_EV_ABORT):
            return "abort"
        else:
            return "abort"

    def print_current_config(self, session, module_name):
        select_xpath = "/" + module_name + ":*//*"

        values = session.get_items(select_xpath)
        if not values:
            sys.stderr.write('print_current_config has a None for values\n')
            return

        for i in range(values.val_cnt()):
            print(values.val(i).to_string(), end='')

    def callback(self, sess, module_name, event, private_ctx):
        sys.stderr.write('Callback has not been over-ridden\n')

        try:
            print("\n\n ========== Notification " + self.ev_to_str(event) + " =============================================\n")
            if (sr.SR_EV_APPLY == event):
                print("\n ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")
                self.print_current_config(sess, module_name)

            print("\n ========== CHANGES: =============================================\n")

            change_path = "/" + module_name + ":*"

            it = sess.get_changes_iter(change_path)

            while True:
                change = sess.get_change_next(it)
                if change == None:
                    break
                self.print_change(change.oper(), change.old_val(), change.new_val())

            print("\n\n ========== END OF CHANGES =======================================\n")

        except Exception as e:
            print(e)

        return sr.SR_ERR_OK
