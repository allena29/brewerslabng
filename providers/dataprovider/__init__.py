#!/usr/bin/python3
import traceback as tb

# import libsysrepoPython3 as sr
import sysrepo as sr
import sys
import time


class DataProvider:

    MODULE_NAME = None
    DEBUG = True

    def connect_oper(self, path):
        self.conn = sr.Connection("oper_%s" % (self.MODULE_NAME))
        self.session = sr.Session(self.conn)
        self.subscribe = sr.Subscribe(self.session)
        self.last_oper_refresh = 0
        self.oper_val_dict = {}
        self.oper_module_path = path
        self.subscribe.dp_get_items_subscribe(path, self.callback_for_oper)
        sr.global_loop()

    def convert_dict_to_oper_values(self, xpath, holder):
        if time.time() - self.last_oper_refresh > 1:
            self.refresh_oper_values(self.oper_val_dict, xpath)
            self.last_oper_refresh = time.time()

        if len(self.oper_val_dict) == 0:
            return

        # TODO: think about filtering here to ensure values only match the requested
        # XPATH - some things might ask for lots of individual paths.
        values = holder.allocate(len(self.oper_val_dict))
        idx = 0
        for val_path in self.oper_val_dict:
            (val, type) = self.oper_val_dict[val_path]
            full_path = self.oper_module_path + val_path
            print('...', full_path, val, type)
            values.val(idx).set(full_path, val, type)
            idx = idx + 1

    def callback_for_oper(private_ctx, xpath, holder, *args):
        private_ctx.convert_dict_to_oper_values(xpath, holder)
        return sr.SR_ERR_OK

    def connect(self):
        self.conn = sr.Connection("provider_%s" % (self.MODULE_NAME))
        self.session = sr.Session(self.conn)
        self.subscribe = sr.Subscribe(self.session)

        self.subscribe.module_change_subscribe(self.MODULE_NAME, self.callback)

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
        try:
            if self.DEBUG:
                self.debug_callback(sess, module_name, event, private_ctx)
            else:

                dry_run = False
                if event == sr.SR_EV_VERIFY:
                    dry_run = True
                else:
                    dry_run = False

                change_path = "/" + module_name + ":*"
                it = sess.get_changes_iter(change_path)
                while True:
                    change = sess.get_change_next(it)
                    if change is None:
                        break

                    xpath = None
                    op = change.oper()
                    oper = 0
                    new_val = None
                    old_val = None
                    if (op == sr.SR_OP_CREATED):
                        new_val = DataProvider.get_data(change.new_val())
                        xpath = change.new_val().xpath()
                        oper = 1
                    elif (op == sr.SR_OP_DELETED):
                        old_val = DataProvider.get_data(change.old_val())
                        xpath = change.old_val().xpath()
                        oper = 2
                    elif (op == sr.SR_OP_MODIFIED):
                        oper = 3
                        new_val = DataProvider.get_data(change.new_val())
                        old_val = DataProvider.get_data(change.old_val())
                        xpath = change.old_val().xpath()

                    if old_val is not None or new_val is not None:
                        self.process_path(dry_run, xpath, oper, old_val, new_val)

        except Exception as e:
            print(e)
            print(tb.format_exc())

            return sr.SR_ERR_OPERATION_FAILED

        return sr.SR_ERR_OK

    @staticmethod
    def get_data(valObject):
        """
        This is a wrapped version of a Val Object object
        http://www.sysrepo.org/static/doc/html/classsysrepo_1_1Data.html
        http://www.sysrepo.org/static/doc/html/group__cl.html#ga5801ac5c6dcd2186aa169961cf3d8cdc

        These don't map directly to the C API
        SR_UINT32_T 20
        SR_CONTAINER_PRESENCE_T 4
        SR_INT64_T 16
        SR_BITS_T 7
        SR_IDENTITYREF_T 11
        SR_UINT8_T 18
        SR_LEAF_EMPTY_T 5
        SR_DECIMAL64_T 9
        SR_INSTANCEID_T 12
        SR_TREE_ITERATOR_T 1
        SR_CONTAINER_T 3
        SR_UINT64_T 21
        SR_INT32_T 15
        SR_ENUM_T 10
        SR_UNKNOWN_T 0
        SR_STRING_T 17
        SR_ANYXML_T 22
        SR_INT8_T 13
        SR_LIST_T 2
        SR_INT16_T 14
        SR_BOOL_T 8
        SR_ANYDATA_T 23
        SR_UINT16_T 19
        SR_BINARY_T 6

        """
        # return valObject.val_to_string()
        if not valObject:
            #print('returning super super early')
            return None
        type = valObject.type()
        if type == sr.SR_STRING_T:
            return valObject.val_to_string()
        elif type == sr.SR_UINT64_T:
            return valObject.data().get_uint64()
        elif type == sr.SR_UINT32_T:
            return valObject.data().get_uint32()
        elif type == sr.SR_UINT16_T:
            return valObject.data().get_uint16()
        elif type == sr.SR_UINT8_T:
            return valObject.data().get_uint8()
        elif type == sr.SR_UINT64_T:
            return valObject.data().get_uint8()
        elif type == sr.SR_INT64_T:
            return valObject.data().get_int64()
        elif type == sr.SR_INT32_T:
            return valObject.data().get_int32()
        elif type == sr.SR_INT16_T:
            return valObject.data().get_int16()
        elif type == sr.SR_INT64_T:
            return valObject.data().get_int8()
        elif type == sr.SR_BOOL_T:
            return valObject.data().get_bool()
        elif type == sr.SR_ENUM_T:
            return valObject.data().get_enum()
        elif type == sr.SR_LIST_T or type == sr.SR_CONTAINER_T:
            #print('container or list - returning nothing')
            return None
        elif type == sr.SR_DECIMAL64_T:
            return valObject.data().get_decimal64()
        elif type == sr.SR_LEAF_EMPTY_T:
            #print('empty leaf returning none')
            return None

        #print('got here without dealing with a type', repr(type), type)

    def debug_callback(self, sess, module_name, event, private_ctx):
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
                if change is None:
                    break
                self.print_change(change.oper(), change.old_val(), change.new_val())

            print("\n\n ========== END OF CHANGES =======================================\n")

        except Exception as e:
            print(e)

        return sr.SR_ERR_OK
