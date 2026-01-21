import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import traceback

# 设置页面
st.set_page_config(
    page_title="股权激励动态管理Demo",
    page_icon="📈",
    layout="wide"
)

# 初始化session state
def init_session_state():
    """安全地初始化所有session state变量"""
    if 'level_standards' not in st.session_state:
        st.session_state.level_standards = {}
    if 'hc_plan' not in st.session_state:
        st.session_state.hc_plan = []
    if 'employees' not in st.session_state:
        st.session_state.employees = []
    if 'equity_grants' not in st.session_state:
        st.session_state.equity_grants = []
    if 'stock_pool_balance' not in st.session_state:
        st.session_state.stock_pool_balance = 0
    if 'stock_pool_total' not in st.session_state:
        st.session_state.stock_pool_total = 0
    if 'operation_history' not in st.session_state:
        st.session_state.operation_history = []
    if 'data_backup' not in st.session_state:
        st.session_state.data_backup = None

init_session_state()

# ========== 辅助函数 ==========
def safe_int(value, default=0):
    """安全地将值转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def calculate_hc_requirement():
    """计算HC规划的总股数需求"""
    if not st.session_state.hc_plan:
        return 0
    
    total_required = 0
    for plan in st.session_state.hc_plan:
        level = plan.get('level', '')
        plan_count = plan.get('plan_count', 0)
        standard = st.session_state.level_standards.get(level, 0)
        total_required += standard * plan_count
    
    return total_required

def calculate_current_usage():
    """计算当前已使用的股数"""
    try:
        return sum(grant.get('shares', 0) for grant in st.session_state.equity_grants)
    except Exception:
        return 0

def update_stock_pool(amount, description, change_type="其他"):
    """更新股票池余额"""
    try:
        st.session_state.stock_pool_balance += amount
        st.session_state.operation_history.append({
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': change_type,
            'description': description,
            'amount': amount,
            'balance': st.session_state.stock_pool_balance
        })
    except Exception as e:
        st.error(f"更新股票池失败: {str(e)}")

def find_employee(employee_id):
    """查找员工"""
    for emp in st.session_state.employees:
        if emp.get('employee_id') == employee_id:
            return emp
    return None

# ========== 侧边栏 ==========
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.header("⚙️ 系统配置")
        
        # 公司信息
        col1, col2 = st.columns(2)
        with col1:
            total_shares = st.number_input("公司总股本（万股）:", 
                                          min_value=1000, 
                                          max_value=1000000, 
                                          value=10000, 
                                          step=1000)
        
        with col2:
            options_pool_pct = st.slider("期权池比例（%）:", 
                                        min_value=5, 
                                        max_value=25, 
                                        value=15, 
                                        step=1)
        
        # 计算股票池
        options_pool_total = int(total_shares * 10000 * options_pool_pct / 100)
        st.session_state.stock_pool_total = options_pool_total
        
        if st.button("初始化股票池", type="primary"):
            st.session_state.stock_pool_balance = options_pool_total
            update_stock_pool(0, f'初始化股票池，总额: {options_pool_total:,}股', '初始化')
            st.success(f"股票池初始化完成！")
        
        # 显示股票池信息
        try:
            current_usage = calculate_current_usage()
            usage_rate = (current_usage / st.session_state.stock_pool_total * 100) if st.session_state.stock_pool_total > 0 else 0
            
            st.info(f"""
            **股票池信息:**
            - 股票池总额: {st.session_state.stock_pool_total:,}股
            - 当前余额: {st.session_state.stock_pool_balance:,}股
            - 已使用: {current_usage:,}股
            - 使用率: {usage_rate:.1f}%
            """)
        except Exception:
            st.warning("无法计算股票池信息")
        
        st.markdown("---")
        st.header("📊 数据管理")
        
        # 数据备份
        if st.button("备份当前数据"):
            try:
                st.session_state.data_backup = {
                    'level_standards': dict(st.session_state.level_standards),
                    'hc_plan': list(st.session_state.hc_plan),
                    'employees': list(st.session_state.employees),
                    'equity_grants': list(st.session_state.equity_grants),
                    'stock_pool_balance': st.session_state.stock_pool_balance,
                    'stock_pool_total': st.session_state.stock_pool_total,
                    'backup_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("数据备份成功！")
            except Exception as e:
                st.error(f"备份失败: {str(e)}")
        
        # 数据恢复
        if st.session_state.data_backup and st.button("恢复备份数据"):
            try:
                backup = st.session_state.data_backup
                st.session_state.level_standards = backup.get('level_standards', {})
                st.session_state.hc_plan = backup.get('hc_plan', [])
                st.session_state.employees = backup.get('employees', [])
                st.session_state.equity_grants = backup.get('equity_grants', [])
                st.session_state.stock_pool_balance = backup.get('stock_pool_balance', 0)
                st.session_state.stock_pool_total = backup.get('stock_pool_total', 0)
                st.success("数据恢复成功！")
                st.rerun()
            except Exception as e:
                st.error(f"恢复失败: {str(e)}")
        
        # 示例数据
        if st.button("生成示例数据", type="primary"):
            try:
                # 生成职级标准
                levels = ['P5', 'P6', 'P7', 'P8', 'M1', 'M2']
                standard_shares = [10000, 20000, 40000, 80000, 50000, 100000]
                st.session_state.level_standards = dict(zip(levels, standard_shares))
                
                # 生成HC规划
                departments = ['研发部', '产品部', '市场部']
                st.session_state.hc_plan = []
                for dept in departments:
                    for level in ['P6', 'P7', 'M1']:
                        st.session_state.hc_plan.append({
                            'department': dept,
                            'level': level,
                            'plan_count': 2,
                            'year': 2024
                        })
                
                # 生成员工
                st.session_state.employees = []
                for i in range(1, 11):
                    dept = departments[i % len(departments)]
                    level = levels[i % len(levels)]
                    status = '在职' if i > 2 else '拟入职'
                    
                    employee = {
                        'employee_id': f'E{i:03d}',
                        'name': f'员工{i}',
                        'department': dept,
                        'level': level,
                        'join_date': '2024-01-01',
                        'status': status
                    }
                    st.session_state.employees.append(employee)
                    
                    # 在职员工授予股权
                    if status == '在职':
                        shares = st.session_state.level_standards.get(level, 0)
                        if shares > 0:
                            st.session_state.equity_grants.append({
                                'grant_id': f'G{len(st.session_state.equity_grants)+1:03d}',
                                'employee_id': employee['employee_id'],
                                'shares': shares,
                                'grant_date': employee['join_date'],
                                'vesting_schedule': '4年匀速',
                                'vested_shares': int(shares * 0.25),  # 假设已归属25%
                                'status': '生效中'
                            })
                
                # 更新股票池
                used_shares = calculate_current_usage()
                st.session_state.stock_pool_balance = max(0, options_pool_total - used_shares)
                update_stock_pool(0, '生成示例数据', '数据生成')
                
                st.success("示例数据生成成功！")
                st.rerun()
            except Exception as e:
                st.error(f"生成示例数据失败: {str(e)}")
        
        # 重置数据
        if st.button("重置所有数据"):
            keys_to_keep = ['data_backup']
            keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_keep]
            
            for key in keys_to_delete:
                del st.session_state[key]
            
            init_session_state()
            st.success("数据已重置！")
            st.rerun()

# ========== 标签页函数 ==========
def render_dashboard():
    """渲染仪表盘"""
    st.header("📊 股权激励管理仪表盘")
    
    try:
        # 关键指标
        total_required = calculate_hc_requirement()
        current_usage = calculate_current_usage()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("HC规划需求", f"{total_required:,} 股")
        
        with col2:
            usage_percent = (current_usage / st.session_state.stock_pool_total * 100) if st.session_state.stock_pool_total > 0 else 0
            st.metric("当前已使用", f"{current_usage:,} 股", f"{usage_percent:.1f}%")
        
        with col3:
            st.metric("股票池余额", f"{st.session_state.stock_pool_balance:,} 股")
        
        with col4:
            if total_required > 0:
                available_rate = (st.session_state.stock_pool_balance / total_required * 100)
                st.metric("可用比例", f"{available_rate:.1f}%")
            else:
                st.metric("可用比例", "100%")
        
        st.markdown("---")
        
        # 可视化图表
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("股票池构成")
            if st.session_state.stock_pool_total > 0:
                labels = ['已使用', '未使用']
                values = [current_usage, st.session_state.stock_pool_balance]
                
                fig = px.pie(values=values, names=labels, hole=0.5,
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
                fig.update_traces(textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("HC需求分析")
            if st.session_state.hc_plan and st.session_state.level_standards:
                # 按部门计算需求
                dept_data = {}
                for plan in st.session_state.hc_plan:
                    dept = plan.get('department', '未知')
                    level = plan.get('level', '')
                    count = plan.get('plan_count', 0)
                    standard = st.session_state.level_standards.get(level, 0)
                    
                    if dept not in dept_data:
                        dept_data[dept] = 0
                    dept_data[dept] += standard * count
                
                if dept_data:
                    df = pd.DataFrame(list(dept_data.items()), columns=['部门', '需求股数'])
                    fig = px.bar(df, x='部门', y='需求股数', color='部门',
                                title="各部门HC需求", text_auto=True)
                    st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"渲染仪表盘时出错: {str(e)}")

def render_level_standards():
    """渲染职级标准页面"""
    st.header("🎯 职级标准设置")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("当前职级标准")
        if st.session_state.level_standards:
            df = pd.DataFrame(list(st.session_state.level_standards.items()), 
                            columns=['职级', '标准股数'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无职级标准数据")
    
    with col2:
        st.subheader("添加/修改标准")
        with st.form("level_form"):
            level = st.text_input("职级", placeholder="如: P7")
            shares = st.number_input("标准股数", min_value=0, value=20000, step=1000)
            
            if st.form_submit_button("保存"):
                if level and level.strip():
                    st.session_state.level_standards[level.strip()] = shares
                    st.success(f"已设置职级 {level} 的标准股数为 {shares:,}股")
                    st.rerun()
                else:
                    st.error("请输入有效的职级")
        
        if st.session_state.level_standards and st.button("清除所有标准"):
            st.session_state.level_standards = {}
            st.rerun()

def render_hc_plan():
    """渲染HC规划页面"""
    st.header("📋 HC规划管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("HC规划列表")
        if st.session_state.hc_plan:
            df = pd.DataFrame(st.session_state.hc_plan)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无HC规划数据")
    
    with col2:
        st.subheader("添加规划")
        with st.form("hc_form"):
            department = st.text_input("部门", placeholder="如: 研发部")
            
            if st.session_state.level_standards:
                level = st.selectbox("职级", list(st.session_state.level_standards.keys()))
            else:
                level = st.text_input("职级", placeholder="如: P7")
                st.warning("请先在'职级标准'页面设置职级标准")
            
            plan_count = st.number_input("计划人数", min_value=1, value=1)
            year = st.number_input("规划年度", min_value=2024, max_value=2030, value=2024)
            
            if st.form_submit_button("添加"):
                if department and department.strip() and level:
                    st.session_state.hc_plan.append({
                        'department': department.strip(),
                        'level': level,
                        'plan_count': plan_count,
                        'year': year
                    })
                    st.success("规划已添加")
                    st.rerun()
                else:
                    st.error("请填写完整的规划信息")
        
        if st.session_state.hc_plan and st.button("清除所有规划"):
            st.session_state.hc_plan = []
            st.rerun()

def render_employee_management():
    """渲染员工管理页面"""
    st.header("👥 员工管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("员工列表")
        if st.session_state.employees:
            df = pd.DataFrame(st.session_state.employees)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无员工数据")
    
    with col2:
        st.subheader("员工操作")
        operation = st.selectbox("选择操作", ["新增员工", "办理入职", "办理离职"])
        
        if operation == "新增员工":
            with st.form("add_employee_form"):
                name = st.text_input("姓名", placeholder="如: 张三")
                department = st.text_input("部门", placeholder="如: 研发部")
                
                if st.session_state.level_standards:
                    level = st.selectbox("职级", list(st.session_state.level_standards.keys()))
                else:
                    st.warning("请先在'职级标准'页面设置职级标准")
                    level = st.text_input("职级", placeholder="如: P7")
                
                status = st.selectbox("状态", ["拟入职", "在职"])
                
                if st.form_submit_button("添加员工"):
                    if name and department and level:
                        emp_id = f"E{len(st.session_state.employees)+1:03d}"
                        new_emp = {
                            'employee_id': emp_id,
                            'name': name.strip(),
                            'department': department.strip(),
                            'level': level,
                            'join_date': datetime.now().strftime("%Y-%m-%d"),
                            'status': status
                        }
                        st.session_state.employees.append(new_emp)
                        
                        # 如果在职，自动授予股权
                        if status == '在职' and level in st.session_state.level_standards:
                            shares = st.session_state.level_standards[level]
                            if shares <= st.session_state.stock_pool_balance:
                                grant_id = f"G{len(st.session_state.equity_grants)+1:03d}"
                                st.session_state.equity_grants.append({
                                    'grant_id': grant_id,
                                    'employee_id': emp_id,
                                    'shares': shares,
                                    'grant_date': datetime.now().strftime("%Y-%m-%d"),
                                    'vesting_schedule': '4年匀速',
                                    'vested_shares': 0,
                                    'status': '生效中'
                                })
                                update_stock_pool(-shares, f"{name}入职授予", "入职授予")
                                st.success(f"员工添加成功，并授予{shares:,}股")
                            else:
                                st.warning("股票池余额不足，员工添加成功但未授予股权")
                        else:
                            st.success("员工添加成功")
                        st.rerun()
                    else:
                        st.error("请填写完整的员工信息")
        
        elif operation == "办理入职":
            pending_employees = [e for e in st.session_state.employees if e.get('status') == '拟入职']
            if pending_employees:
                employee_options = [f"{e.get('name', '')} ({e.get('employee_id', '')})" for e in pending_employees]
                selected = st.selectbox("选择拟入职员工", employee_options)
                
                if selected and st.button("办理入职"):
                    try:
                        emp_id = selected.split('(')[-1].rstrip(')')
                        for emp in st.session_state.employees:
                            if emp.get('employee_id') == emp_id:
                                emp['status'] = '在职'
                                emp['join_date'] = datetime.now().strftime("%Y-%m-%d")
                                
                                # 授予股权
                                level = emp.get('level', '')
                                if level in st.session_state.level_standards:
                                    shares = st.session_state.level_standards[level]
                                    if shares <= st.session_state.stock_pool_balance:
                                        grant_id = f"G{len(st.session_state.equity_grants)+1:03d}"
                                        st.session_state.equity_grants.append({
                                            'grant_id': grant_id,
                                            'employee_id': emp_id,
                                            'shares': shares,
                                            'grant_date': datetime.now().strftime("%Y-%m-%d"),
                                            'vesting_schedule': '4年匀速',
                                            'vested_shares': 0,
                                            'status': '生效中'
                                        })
                                        update_stock_pool(-shares, f"{emp.get('name')}入职授予", "入职授予")
                                        st.success(f"已办理入职并授予{shares:,}股")
                                    else:
                                        st.error("股票池余额不足")
                                else:
                                    st.warning("该职级标准未设置")
                                break
                        st.rerun()
                    except Exception as e:
                        st.error(f"办理入职失败: {str(e)}")
            else:
                st.info("暂无拟入职员工")
        
        elif operation == "办理离职":
            active_employees = [e for e in st.session_state.employees if e.get('status') == '在职']
            if active_employees:
                employee_options = [f"{e.get('name', '')} ({e.get('employee_id', '')})" for e in active_employees]
                selected = st.selectbox("选择离职员工", employee_options)
                
                if selected and st.button("办理离职"):
                    try:
                        emp_id = selected.split('(')[-1].rstrip(')')
                        for emp in st.session_state.employees:
                            if emp.get('employee_id') == emp_id:
                                emp['status'] = '离职'
                                emp['leave_date'] = datetime.now().strftime("%Y-%m-%d")
                                
                                # 回收未归属股权
                                total_unvested = 0
                                for grant in st.session_state.equity_grants:
                                    if grant.get('employee_id') == emp_id and grant.get('status') == '生效中':
                                        vested = grant.get('vested_shares', 0)
                                        unvested = grant.get('shares', 0) - vested
                                        total_unvested += unvested
                                        grant['status'] = '已终止'
                                
                                if total_unvested > 0:
                                    update_stock_pool(total_unvested, f"{emp.get('name')}离职回收", "离职回收")
                                    st.success(f"已办理离职，回收{total_unvested:,}股未归属股权")
                                else:
                                    st.success("已办理离职")
                                break
                        st.rerun()
                    except Exception as e:
                        st.error(f"办理离职失败: {str(e)}")
            else:
                st.info("暂无在职员工")

def render_equity_grants():
    """渲染股权授予页面"""
    st.header("📈 股权授予管理")
    
    if st.session_state.equity_grants:
        try:
            # 准备显示数据
            grants_data = []
            for grant in st.session_state.equity_grants:
                emp = find_employee(grant.get('employee_id', ''))
                row = grant.copy()
                row['员工姓名'] = emp.get('name', '未知') if emp else '未知'
                row['部门'] = emp.get('department', '未知') if emp else '未知'
                row['未归属股数'] = grant.get('shares', 0) - grant.get('vested_shares', 0)
                grants_data.append(row)
            
            df = pd.DataFrame(grants_data)
            st.dataframe(df, use_container_width=True)
            
            # 统计信息
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("总授予数", len(df))
            
            with col2:
                total_shares = df['shares'].sum()
                st.metric("总授予股数", f"{total_shares:,}股")
            
            with col3:
                vested_shares = df['vested_shares'].sum()
                st.metric("已归属股数", f"{vested_shares:,}股")
            
            with col4:
                unvested_shares = df['未归属股数'].sum()
                st.metric("未归属股数", f"{unvested_shares:,}股")
        
        except Exception as e:
            st.error(f"显示股权授予数据时出错: {str(e)}")
    else:
        st.info("暂无股权授予记录")

def render_monitoring():
    """渲染动态监控页面"""
    st.header("📈 动态监控")
    
    if st.session_state.operation_history:
        try:
            # 操作历史
            df = pd.DataFrame(st.session_state.operation_history)
            st.subheader("操作历史")
            st.dataframe(df.sort_values('time', ascending=False), use_container_width=True)
            
            # 简单统计
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("操作总数", len(df))
            
            with col2:
                # 今日操作数
                today = datetime.now().strftime("%Y-%m-%d")
                today_count = sum(1 for op in st.session_state.operation_history 
                                if op.get('time', '').startswith(today))
                st.metric("今日操作", today_count)
            
            with col3:
                # 最近流入流出
                recent = df.tail(10) if len(df) > 10 else df
                inflow = recent[recent['amount'] > 0]['amount'].sum()
                outflow = abs(recent[recent['amount'] < 0]['amount'].sum())
                st.metric("近期变动", f"+{inflow:,}/-{outflow:,}")
        
        except Exception as e:
            st.error(f"显示监控数据时出错: {str(e)}")
    else:
        st.info("暂无操作历史")

# ========== 主应用 ==========
def main():
    """主应用函数"""
    st.title("🏢 股权激励动态管理Demo")
    st.markdown("---")
    
    # 渲染侧边栏
    render_sidebar()
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 仪表盘", "🎯 职级标准", "📋 HC规划", 
        "👥 员工管理", "📈 股权授予", "📈 动态监控"
    ])
    
    # 渲染各标签页
    with tab1:
        render_dashboard()
    
    with tab2:
        render_level_standards()
    
    with tab3:
        render_hc_plan()
    
    with tab4:
        render_employee_management()
    
    with tab5:
        render_equity_grants()
    
    with tab6:
        render_monitoring()
    
    # 底部信息
    st.markdown("---")
    st.caption("🏢 股权激励动态管理Demo | 简化版本 v1.0")

# 运行应用
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"应用运行时出错: {str(e)}")
        with st.expander("错误详情"):
            st.code(traceback.format_exc())
