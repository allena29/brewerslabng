import sysrepo as sr
import sys
print('past imports')

# Helper function for printing changes given operation, old and new value.

FLUSH = sys.stdout.flush

def print_change(op, old_val, new_val):
    if op == sr.SR_OP_CREATED:
        print("CREATED:")
        print(new_val.to_string(), end="")
    elif op == sr.SR_OP_DELETED:
        print("DELETED:")
        print(old_val.to_string(), end="")
    elif op == sr.SR_OP_MODIFIED:
        print("MODIFIED:")
        print("old value", end="")
        print(old_val.to_string(), end="")
        print("new value", end="")
        print(new_val.to_string(), end="")
    elif op == sr.SR_OP_MOVED:
        print("MOVED:\n", new_val.get_xpath(), " after ", old_val.get_xpath())
    print("")

# Helper function for printing events.
def ev_to_str(ev):
    if (ev == sr.SR_EV_VERIFY):
        return "verify"
    elif (ev == sr.SR_EV_APPLY):
        return "apply"
    elif (ev == sr.SR_EV_ABORT):
        return "abort"
    else:
        return "abort"

# Function to print current configuration state.
# It does so by loading all the items of a session and printing them out.
def print_current_config(session, module_name):
    select_xpath = "/" + module_name + ":*//*"

    values = session.get_items(select_xpath)

    for i in range(values.val_cnt()):
        print(values.val(i).to_string(), end="")

def test_rpc_cb(xpath, in_vals, out_vals, private_ctx):
    print("\n\n ========== RPC CALLED for removing food==========")

def module_change_cb(sess, module_name, event, private_ctx):
    print ("\n\n ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")

    try:
        print ("\n\n ========== Notification " + ev_to_str(event) + " =============================================\n")
        if (sr.SR_EV_APPLY == event):
            print
            "\n ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n"
            print_current_config(sess, module_name);

        print ("\n ========== CHANGES: =============================================\n")

        change_path = "/" + module_name + ":*"

        it = sess.get_changes_iter(change_path);

        while True:
            change = sess.get_change_next(it)
            if change == None:
                break
            print_change(change.oper(), change.old_val(), change.new_val())

        print("\n\n ========== END OF CHANGES =======================================\n")

    except Exception as e:
        print(e)

    return sr.SR_ERR_OK

def oven_state_cb(xpath, holder, private_ctx, *args):
    print("\n\n ========== OVEN State queried ==========")
    for x in args:
        print(x)
    values = holder.allocate(2)
    values.val(0).set('/oven:oven-state/temperature', 3, sr.SR_UINT8_T)
    values.val(1).set("/oven:oven-state/food-inside", True, sr.SR_BOOL_T)
    return sr.SR_ERR_OK

if __name__ == '__main__':
    conn = sr.Connection("test-daemon")
    session = sr.Session(conn)
    subscribe = sr.Subscribe(session)
    print(subscribe)
    subscribe.module_change_subscribe("oven", module_change_cb)

    subscribe.rpc_subscribe("/oven:remove-food", test_rpc_cb)
    
    subscribe.dp_get_items_subscribe('/oven:oven-state', oven_state_cb)
    print('subscribe for state done')

    sr.global_loop()

