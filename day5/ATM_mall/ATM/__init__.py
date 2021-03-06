#! /usr/bin/env python3

from publicAPI import auth_account, register_account, change_admin_password
from publicAPI import modify_admin_account_info, add_admin_account, delete_account, change_admin_permission
from config.settings import user_info
from publicAPI import register_account, for_super_admin_change_password, for_admin_unlock_account, for_admin_lock_account
from record_log import Logger
from publicAPI import change_user_credit_line, show_account_info, for_owner_change_password
from publicAPI import transfer_cash, search_history_log
from publicAPI import for_admin_withdraw_money
bank_log_file = "china_bank.log"  # 银行基本日志
sold_log_file = "sold_bank.log"  # 用户交易日志


def update_info(user_info_dict, file_path="./config/settings.py", name="user_info = "):  # 接收一个字典字符串,然后写入到文件,把一个字典类型参数写入文件
    import re
    write_data = re.findall('["\'\[\]\w,:\s=\d@.\-]+\{*|\}', name + str(user_info_dict).replace("'", '"'))
    count = 0
    with open(file_path, 'w') as database:
        for content in write_data:
            if content.find('{') != -1:
                database.write('%s%s\n' % (str(count * '\t').expandtabs(4), content))
                count += 1
            elif content.find('}') != -1:
                database.write('%s%s\n' % (str(count * '\t').expandtabs(4), content))
                count -= 1
            else:
                database.write('%s%s\n' % (str(count * '\t').expandtabs(4), content))
    database.close()
    return True


def atm_self_service(quit_atm_self_service=False):  # ATM自助服务系统
    while not quit_atm_self_service:
        print("""欢迎使用    中国建都银行    自助服务系统
        ============================================
        普通客户大众版平台(1)    银行前台专业版管理中心(2)
        返回(b)    退出(q)
        ============================================
        """)
        wait_choose = str(input("请选择操作:")).strip()
        if wait_choose == "1":
            Logger(bank_log_file).write_log(status=True, event="进入普通客户大众版平台")
            quit_atm_self_service = public_login(bank_log_file, quit_atm_self_service)  # 进入大众版登陆系统
        elif wait_choose == "2":
            Logger(bank_log_file).write_log(user=None, status=True, event="进入银行前台管理页面")
            quit_atm_self_service = admin_bank_system(bank_log_file, quit_atm_self_service)  # 进入管理员操作平台
        elif str(wait_choose).lower() in ['q', 'quit', ]:
            quit_atm_self_service = True
            print("谢谢使用,再见 !")
            Logger(bank_log_file).write_log(status=True, event="退出")
            break
        elif str(wait_choose).lower() in ['b', 'back', ]:
            break
        else:
            print("操作有误 !!!")
    return quit_atm_self_service


def public_login(log_file, quit_public_login=False):
    while not quit_public_login:
        try:
            user_database = user_info["user_bank"]
        except KeyError:
            user_info["user_bank"] = {}
            user_database = user_info["user_bank"]
        print("""欢迎进入    中国建都银行    用户中心
        =========================================
        用户登陆(1)
        返回(b)  退出(q)
        =========================================
        """)
        wait_choose = str(input("请选择操作:")).strip()
        if wait_choose == "1":
            get_user = auth_account(user_database, log_file=log_file)
            if type(get_user) == dict:  # 如果有数据返回,且不是True,则该账户被锁定,写入数据
                user_info["user_bank"] = get_user
                update_info(user_info)
            elif get_user:
                try:
                    user_status = user_info["user_bank"][get_user]["user_status"]
                    if user_status == "0":  # 当登陆成功后,重置用户登陆错误状态
                        user_info["user_bank"][get_user]["user_status"] = "2"
                        update_info(user_info)
                except KeyError:
                    pass
                quit_public_login = public_user_system(get_user, quit_public_login, log_file)
        elif str(wait_choose).lower() in ['q', 'quit', ]:
            quit_public_login = True
            print("谢谢使用,再见 !")
            Logger(log_file).write_log(status=True, event="退出")
            break
        elif str(wait_choose).lower() in ['b', 'back', ]:
            break
        else:
            print("操作有误 !!!")
    return quit_public_login


def public_user_system(user, quit_user_system=False, log_file=None):
    while not quit_user_system:
        user_database = user_info["user_bank"]
        print("""欢迎使用    中国建都银行    用户[%s]已登陆
        ===============================================
        个人信息(1)  修改密码(2)
        转账(3)  取现(4)  还款(5)
        交易记录(6)  操作日志(7)
        账单查询(8)
        注销(b)  退出(q)
        ===============================================
        """ % user)
        wait_choose = str(input("请选择操作:")).strip()
        if wait_choose == "1":
            show_account_info(user_database, user, is_admin=False, log_file=log_file)
        elif wait_choose == "2":
            get_database = for_owner_change_password(user_database, user, log_file=log_file)
            if type(get_database) == dict:
                user_info["user_bank"] = get_database
                update_info(user_info)
        elif wait_choose == "3":
            get_database = transfer_cash(user_database, user, log_file=log_file, sold_log=sold_log_file)
            if type(get_database) == dict:
                user_info["user_bank"] = get_database
                update_info(user_info)
        elif wait_choose == "4":
            get_database = for_admin_withdraw_money(user_database, user, log_file=log_file, sold_log= sold_log_file)
            if type(get_database) == dict:
                user_info["user_bank"] = get_database
                update_info(user_info)
        elif wait_choose == "6":
            search_history_log(user, log_file=log_file, sold_log=sold_log_file, is_sold=True)
        elif wait_choose == "7":
            search_history_log(user, log_file=log_file)
        elif str(wait_choose).lower() in ['q', 'quit', ]:
            quit_user_system = True
            print("谢谢使用,再见 !")
            Logger(log_file).write_log(user=user, status=True, event="退出")
            break
        elif str(wait_choose).lower() in ['b', 'back', ]:
            break
        else:
            print("操作有误 !!!")
    return quit_user_system


def admin_bank_system(log_file, quit_admin_bank=False):  # 银行管理人员操作平台
    while not quit_admin_bank:
        open_register = "首次注册(2)"
        try:
            admin_database = user_info['admin_bank']
        except KeyError:
            user_info['admin_bank'] = {}
            admin_database = user_info['admin_bank']
        if len(admin_database) > 0:
            open_register = False  # 如果系统存在管理员帐号,则不开放这个功能,后续增加管理员帐号只能登陆后添加
            open_login = "管理员登录(1)"
        else:
            open_login, open_register = open_register, True
        print("""欢迎进入    中国建都银行    管理平台
        ============================================
        %s
        返回(b)    退出(q)
        ============================================
        """ % open_login)
        wait_choose = str(input("请选择操作:")).strip()
        if wait_choose == "1" and not open_register:
            get_admin = auth_account(admin_database, is_admin=True, log_file=log_file)  # 调用登陆模块
            if get_admin:
                quit_admin_bank = admin_management(get_admin, quit_admin_bank, log_file=log_file)  # 进入管理员操作中心
        elif wait_choose == "2" and open_register:  # 只有数据库没有任何用户的情况才会开放这个注册功能
            get_database = register_account(admin_database, is_admin=True, log_file=log_file)  # 调用注册模块
            if get_database:
                user_info['admin_bank'] = get_database  # 更新数据库信息
                update_info(user_info)  # 写入数据库
        elif str(wait_choose).lower() in ['q', 'quit', ]:
            quit_admin_bank = True
            print("谢谢使用,再见 !")
            Logger(log_file).write_log(status=True, event="退出")
            break
        elif str(wait_choose).lower() in ['b', 'back', ]:
            break
        else:
            print("操作有误 !!!")
    return quit_admin_bank


def admin_management(admin_name, quit_admin_management=False, log_file=None):  # 管理员登陆成功后的账号操作
    while not quit_admin_management:
        try:
            user_database = user_info["user_bank"]
        except KeyError:
            user_info["user_bank"] = {}
            user_database = user_info["user_bank"]
        if not user_info["admin_bank"].get(admin_name):
            break
        print("""中国建都银行    管理中心    [%s]已登陆
        ===========================================
        开户(1)  修改密码(2)  查询账户(s)
        存钱(3)  取钱(4)
        额度(5)  解锁(6)
        挂失(7)  销户(8)
        管理员帐户管理(9)
        注销(b)  退出(q)
        ===========================================
        """ % admin_name)
        wait_choose = str(input("请选择操作:")).strip()
        if wait_choose == "1":
            get_database = register_account(user_database, log_file=log_file)
            if type(get_database) == dict:
                user_info["user_bank"] = get_database
                update_info(user_info)
        elif wait_choose == "2":
            get_database = for_super_admin_change_password(user_database, admin_name, log_file=log_file)
            if type(get_database) == dict:
                user_info["user_bank"] = get_database
                update_info(user_info)
        elif wait_choose == "3":
            print("该功能暂未开放")
        elif wait_choose == "4":
            print("该功能暂未开放")
        elif wait_choose.lower() == "s":
            show_account_info(user_database, admin_name, is_admin=True, log_file=log_file)
        elif wait_choose == "5":
            get_database = change_user_credit_line(user_database, admin_name, log_file=log_file)
            if type(get_database) == dict:
                user_info['user_bank'] = get_database  # 更新数据库信息
                update_info(user_info)
        elif wait_choose == "6":
            get_database = for_admin_unlock_account(user_database, admin_name, log_file=log_file)
            if type(get_database) == dict:
                user_info["user_bank"] = get_database
                update_info(user_info)
        elif wait_choose == "7":
            get_database = for_admin_lock_account(user_database, admin_name, log_file=log_file)
            if type(get_database) == dict:
                user_info["user_bank"] = get_database
                update_info(user_info)
        elif wait_choose == "8":
            get_database = delete_account(user_database, admin_name, is_admin=False, log_file=log_file)
            if type(get_database) == dict:
                user_info['user_bank'] = get_database  # 更新数据库信息
                update_info(user_info)
        elif wait_choose == "9":
            quit_admin_management = management_admin_account(
                admin_name, quit_admin_management, log_file=log_file)  # 对管理员账号进行操作
        elif str(wait_choose).lower() in ['q', 'quit', ]:
            quit_admin_management = True
            Logger(log_file).write_log(user=admin_name, status=True, event="管理员退出")
            print("谢谢使用,再见 !")
            break
        elif str(wait_choose).lower() in ['b', 'back', ]:
            Logger(log_file).write_log(user=admin_name, status=True, event="管理员注销")
            break
        else:
            print("操作有误 !!!")
    return quit_admin_management


def management_admin_account(admin_name, quit_management_account, log_file=None):
    while not quit_management_account:
        admin_database = user_info['admin_bank']
        if not admin_database.get(admin_name):
            break
        print("""中国建都银行    管理中心    [%s]已登陆
        ===========================================
        添加管理账号(1)
        删除管理账号(2)
        更改账号权限(3)
        更改账号信息(4)
        修改管理员密码(5)
        返回(b)  退出(q)
        ===========================================
        """ % admin_name)
        wait_choose = str(input("请选择操作:")).strip()
        if wait_choose == "1":
            get_database = add_admin_account(admin_database, admin_name, is_admin=True, log_file=log_file)
            if type(get_database) == dict:
                user_info['admin_bank'] = get_database  # 更新数据库信息
                update_info(user_info)
        elif wait_choose == "2":
            get_database = delete_account(admin_database, admin_name, is_admin=True, log_file=log_file)
            if type(get_database) == dict:
                user_info['admin_bank'] = get_database  # 更新数据库信息
                update_info(user_info)
        elif wait_choose == "3":
            get_database = change_admin_permission(admin_database, admin_name, log_file=log_file)
            if type(get_database) == dict:
                user_info['admin_bank'] = get_database  # 更新数据库信息
                update_info(user_info)
        elif wait_choose == "4":
            get_database = modify_admin_account_info(admin_database, admin_name, is_admin=True, log_file=log_file)
            if type(get_database) == dict:
                user_info['admin_bank'] = get_database  # 更新数据库信息
                update_info(user_info)
        elif wait_choose == "5":
            get_database = change_admin_password(admin_database, admin_name, log_file=log_file)
            if type(get_database) == dict:
                user_info['admin_bank'] = get_database  # 更新数据库信息
                update_info(user_info)
        elif str(wait_choose).lower() in ['q', 'quit', ]:
            quit_management_account = True
            Logger(log_file).write_log(user=admin_name, status=True, event="管理员退出")
            print("谢谢使用,再见 !")
            break
        elif str(wait_choose).lower() in ['b', 'back', ]:
            break
        else:
            print("操作有误 !!!")
    return quit_management_account
