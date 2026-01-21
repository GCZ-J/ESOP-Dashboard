import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json

# ========== 页面配置 ==========
st.set_page_config(
    page_title="股权激励动态管理Demo",
    page_icon="📈",
    layout="wide"
)

st.title("🏢 股权激励动态管理Demo")
st.markdown("---")

# ========== 初始化session state ==========
def init_session_state():
    """初始化session state"""
    defaults = {
        'level_standards': {},
        'hc_plan': [],
        'employees': [],
        'equity_grants': [],
        'stock_pool_balance': 0,
        'stock_pool_total': 0,
        'operation_history': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ========== 数据管理函数 ==========
def save_data_to_session():
    """保存当前数据到session的备份"""
    st.session_state.data_backup = {
        'level_standards': st.session_state.level_standards.copy(),
        'hc_plan': st.session_state.hc_plan.copy(),
        'employees': st.session_state.employees.copy(),
        'equity_grants': st.session_state.equity_grants.copy(),
        'stock_pool_balance': st.session_state.stock_pool_balance,
        'stock_pool_total': st.session_state.stock_pool_total,
        'operation_history': st.session_state.operation_history.copy()
    }

def load_data_from_backup():
    """从备份恢复数据"""
    if hasattr(st.session_state, 'data_backup'):
        backup = st.session_state.data_backup
        for key in backup:
            st.session_state[key] = backup[key]
        return True
    return False

def export_to_json():
    """导出数据为JSON"""
    data = {
        'level_standards': st.session_state.level_standards,
        'hc_plan': st.session_state.hc_plan,
        'employees': st.session_state.employees,
        'equity_grants': st.session_state.equity_grants,
        'stock_pool_balance': st.session_state.stock_pool_balance,
        'stock_pool_total': st.session_state.stock_pool_total,
        'export_time': datetime.now().isoformat()
    }
    return json.dumps(data, indent=2, ensure_ascii=False)

# ========== 业务逻辑函数 ==========
def calculate_hc_requirement():
    """计算HC规划的总股数需求"""
    if not st.session_state.hc_plan:
        return 0
    
    total = 0
    for plan in st.session_state.hc_plan:
        standard = st.session_state.level_standards.get(plan['level'], 0)
        total += standard * plan['plan_count']
    return total

def calculate_current_usage():
    """计算当前已使用的股数"""
    return sum(grant['shares'] for grant in st.session_state.equity_grants)

def update_stock_pool(amount, description, change_type="其他"):
    """更新股票池余额"""
    st.session_state.stock_pool_balance += amount
    st.session_state.operation_history.append({
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': change_type,
        'description': description,
        'amount': amount,
        'balance': st.session_state.stock_pool_balance
    })

def find_employee(employee_id):
    """查找员工"""
    for emp in st.session_state.employees:
        if emp['employee_id'] == employee_id:
            return emp
    return None

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 公司信息
    col1, col2 = st.columns(2)
    with col1:
        total_shares = st.number_input("公司总股本（万股）:", 1000, 1000000, 10000, 1000)
    
    with col2:
        options_pool_pct = st.slider("期权池比例（%）:", 5, 25, 15, 1)
    
    # 计算股票池
    options_pool_total = int(total_shares * 10000 * options_pool_pct / 100)
    st.session_state.stock_pool_total = options_pool_total
    
    if st.button("初始化股票池", type="primary"):
        st.session_state.stock_pool_balance = options_pool_total
        update_stock_pool(0, f'初始化股票池，总额: {options_pool_total:,}股', '初始化')
        st.success(f"股票池初始化完成！总额: {options_pool_total:,}股")
    
    # 股票池信息显示
    used = calculate_current_usage()
    usage_rate = (used / options_pool_total * 100) if options_pool_total > 0 else 0
    
    st.info(f"""
    **股票池信息:**
    - 总股本: {total_shares:,}万股
    - 期权池比例: {options_pool_pct}%
    - 股票池总额: {options_pool_total:,}股
    - 当前余额: {st.session_state.stock_pool_balance:,}股
    - 使用率: {usage_rate:.1f}%
    """)
    
    st.markdown("---")
    
    # 数据管理
    st.header("📊 数据管理")
    
    # 数据备份/恢复
    col1, col2 = st.columns(2)
    with col1:
        if st.button("备份当前数据"):
            save_data_to_session()
            st.success("数据已备份！")
    
    with col2:
        if st.button("恢复备份数据") and load_data_from_backup():
            st.success("数据已恢复！")
            st.rerun()
    
    # 数据导出
    if st.button("导出数据为JSON"):
        st.download_button(
            label="📥 下载JSON",
            data=export_to_json(),
            file_name=f"equity_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # 示例数据生成
    if st.button("生成示例数据", type="primary"):
        # 职级标准
        levels = ['P5', 'P6', 'P7', 'P8', 'P9', 'M1', 'M2', 'M3']
        standard_shares = [10000, 20000, 40000, 80000, 150000, 50000, 100000, 200000]
        st.session_state.level_standards = dict(zip(levels, standard_shares))
        
        # HC规划
        departments = ['研发部', '产品部', '市场部', '销售部']
        st.session_state.hc_plan = [
            {'department': dept, 'level': level, 'plan_count': np.random.randint(1, 3), 'year': 2024}
            for dept in departments for level in ['P6', 'P7', 'M1']
        ]
        
        # 员工数据
        st.session_state.employees = []
        for i in range(1, 21):
            dept = np.random.choice(departments)
            level = np.random.choice(['P6', 'P7', 'M1'])
            status = np.random.choice(['在职', '在职', '拟入职'], p=[0.8, 0.8, 0.2])
            
            emp = {
                'employee_id': f'E{i:03d}',
                'name': f'员工{i}',
                'department': dept,
                'level': level,
                'join_date': f'202{np.random.randint(2,4)}-{np.random.randint(1,13):02d}-01',
                'status': status
            }
            
            if status == '离职':
                emp['leave_date'] = f'2023-{np.random.randint(1,13):02d}-01'
            
            st.session_state.employees.append(emp)
            
            # 股权授予
            if status == '在职' and np.random.random() > 0.4:
                shares = st.session_state.level_standards.get(level, 0)
                if shares > 0:
                    st.session_state.equity_grants.append({
                        'grant_id': f'G{len(st.session_state.equity_grants)+1:03d}',
                        'employee_id': emp['employee_id'],
                        'shares': shares,
                        'grant_date': emp['join_date'],
                        'vesting_schedule': '4年匀速',
                        'vested_shares': int(shares * np.random.uniform(0.1, 0.5)),
                        'status': '生效中'
                    })
        
        # 更新股票池
        used_shares = calculate_current_usage()
        st.session_state.stock_pool_balance = options_pool_total - used_shares
        update_stock_pool(0, '生成示例数据', '数据生成')
        
        st.success("示例数据生成完成！")
        st.rerun()
    
    if st.button("重置所有数据"):
        for key in list(st.session_state.keys()):
            if key != 'data_backup':  # 保留备份
                del st.session_state[key]
        init_session_state()
        st.rerun()

# ========== 仪表盘 ==========
def render_dashboard():
    st.header("📊 股权激励管理仪表盘")
    
    # 关键指标
    total_required = calculate_hc_requirement()
    current_usage = calculate_current_usage()
    
    cols = st.columns(4)
    metrics = [
        ("HC规划需求", f"{total_required:,} 股", None),
        ("当前已使用", f"{current_usage:,} 股", 
         f"{current_usage/st.session_state.stock_pool_total*100 if st.session_state.stock_pool_total > 0 else 0:.1f}%"),
        ("股票池余额", f"{st.session_state.stock_pool_balance:,} 股",
         f"{st.session_state.stock_pool_balance/st.session_state.stock_pool_total*100 if st.session_state.stock_pool_total > 0 else 0:.1f}%"),
        ("可用比例", 
         f"{st.session_state.stock_pool_balance/total_required*100 if total_required > 0 else 100:.1f}%",
         f"剩余 {st.session_state.stock_pool_balance:,} 股")
    ]
    
    for col, (title, value, delta) in zip(cols, metrics):
        with col:
            st.metric(title, value, delta)
    
    st.markdown("---")
    
    # 可视化图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("股票池构成")
        if st.session_state.stock_pool_total > 0:
            labels = ['已使用', '未使用']
            values = [current_usage, st.session_state.stock_pool_balance]
            
            fig = px.pie(values=values, names=labels, hole=0.5,
                        color_discrete_sequence=['#EF553B', '#00CC96'])
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("HC需求 vs 当前使用")
        if st.session_state.hc_plan:
            dept_data = {}
            for plan in st.session_state.hc_plan:
                dept = plan['department']
                if dept not in dept_data:
                    dept_data[dept] = {'requirement': 0, 'usage': 0}
                dept_data[dept]['requirement'] += st.session_state.level_standards.get(plan['level'], 0) * plan['plan_count']
            
            # 计算各部门当前使用
            for grant in st.session_state.equity_grants:
                emp = find_employee(grant['employee_id'])
                if emp and emp['status'] == '在职':
                    dept = emp['department']
                    if dept in dept_data:
                        dept_data[dept]['usage'] += grant['shares']
            
            dept_list = list(dept_data.keys())
            requirement_values = [dept_data[d]['requirement'] for d in dept_list]
            usage_values = [dept_data[d]['usage'] for d in dept_list]
            
            fig = go.Figure(data=[
                go.Bar(name='HC需求', x=dept_list, y=requirement_values),
                go.Bar(name='当前使用', x=dept_list, y=usage_values)
            ])
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)

# ========== 职级标准 ==========
def render_level_standards():
    st.header("🎯 职级标准设置")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("当前职级标准")
        if st.session_state.level_standards:
            df = pd.DataFrame(list(st.session_state.level_standards.items()), 
                            columns=['职级', '标准股数'])
            st.dataframe(df, use_container_width=True)
    
    with col2:
        st.subheader("添加/修改标准")
        with st.form("level_form"):
            level = st.text_input("职级", placeholder="如: P7, M2")
            shares = st.number_input("标准股数", 0, 1000000, 20000, 1000)
            
            if st.form_submit_button("保存"):
                if level:
                    st.session_state.level_standards[level] = shares
                    st.success(f"已设置职级 {level} 的标准股数为 {shares:,}股")
                    st.rerun()
        
        if st.session_state.level_standards:
            if st.button("清除所有标准"):
                st.session_state.level_standards = {}
                st.rerun()
    
    # 图表展示
    if st.session_state.level_standards:
        st.subheader("职级标准分析")
        levels_df = pd.DataFrame([
            {'职级': k, '标准股数': v, '类型': '管理' if k.startswith('M') else '专业'}
            for k, v in st.session_state.level_standards.items()
        ])
        
        fig = px.bar(levels_df, x='职级', y='标准股数', color='类型',
                    title="各职级标准股数对比")
        st.plotly_chart(fig, use_container_width=True)

# ========== HC规划 ==========
def render_hc_plan():
    st.header("📋 HC规划管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("HC规划列表")
        if st.session_state.hc_plan:
            df = pd.DataFrame(st.session_state.hc_plan)
            if st.session_state.level_standards:
                df['单人员工股数'] = df['level'].map(st.session_state.level_standards).fillna(0)
                df['总需求股数'] = df['plan_count'] * df['单人员工股数']
            st.dataframe(df, use_container_width=True)
    
    with col2:
        st.subheader("添加规划")
        with st.form("hc_form"):
            department = st.text_input("部门")
            
            if st.session_state.level_standards:
                level = st.selectbox("职级", list(st.session_state.level_standards.keys()))
            else:
                level = st.text_input("职级")
            
            plan_count = st.number_input("计划人数", 1, 100, 1)
            year = st.number_input("规划年度", 2024, 2030, 2024)
            
            if st.form_submit_button("添加"):
                if department and level:
                    st.session_state.hc_plan.append({
                        'department': department,
                        'level': level,
                        'plan_count': plan_count,
                        'year': year
                    })
                    st.success("规划已添加")
                    st.rerun()
        
        if st.session_state.hc_plan and st.button("清除所有规划"):
            st.session_state.hc_plan = []
            st.rerun()
    
    # 分析图表
    if st.session_state.hc_plan:
        st.subheader("规划分析")
        df = pd.DataFrame(st.session_state.hc_plan)
        dept_summary = df.groupby('department')['plan_count'].sum().reset_index()
        
        fig = px.bar(dept_summary, x='department', y='plan_count',
                    title="各部门规划招聘人数", color='department')
        st.plotly_chart(fig, use_container_width=True)

# ========== 员工管理 ==========
def render_employee_management():
    st.header("👥 员工管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("员工列表")
        if st.session_state.employees:
            df = pd.DataFrame(st.session_state.employees)
            st.dataframe(df, use_container_width=True)
    
    with col2:
        st.subheader("员工操作")
        operation = st.radio("操作", ["新增员工", "办理入职", "办理离职", "办理晋升"])
        
        if operation == "新增员工":
            with st.form("add_emp_form"):
                name = st.text_input("姓名")
                department = st.text_input("部门")
                
                if st.session_state.level_standards:
                    level = st.selectbox("职级", list(st.session_state.level_standards.keys()))
                else:
                    level = st.text_input("职级")
                
                join_date = st.date_input("入职日期", datetime.now())
                status = st.selectbox("状态", ["拟入职", "在职"])
                
                if st.form_submit_button("添加"):
                    if name and department:
                        emp_id = f"E{len(st.session_state.employees)+1:03d}"
                        new_emp = {
                            'employee_id': emp_id,
                            'name': name,
                            'department': department,
                            'level': level,
                            'join_date': join_date.strftime("%Y-%m-%d"),
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
                                    'grant_date': join_date.strftime("%Y-%m-%d"),
                                    'vesting_schedule': '4年匀速',
                                    'vested_shares': 0,
                                    'status': '生效中'
                                })
                                update_stock_pool(-shares, f"{name}入职授予", "入职授予")
                                st.success(f"已自动授予{shares:,}股")
                            else:
                                st.warning("股票池余额不足")
                        st.rerun()
        
        elif operation == "办理入职":
            pending = [e for e in st.session_state.employees if e['status'] == '拟入职']
            if pending:
                selected = st.selectbox("选择员工", [f"{e['name']} ({e['employee_id']})" for e in pending])
                if st.button("办理入职"):
                    emp_id = selected.split('(')[-1].rstrip(')')
                    for emp in st.session_state.employees:
                        if emp['employee_id'] == emp_id:
                            emp['status'] = '在职'
                            # 授予股权
                            shares = st.session_state.level_standards.get(emp['level'], 0)
                            if shares > 0:
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
                                update_stock_pool(-shares, f"{emp['name']}入职授予", "入职授予")
                            break
                    st.success("已办理入职")
                    st.rerun()
        
        elif operation == "办理离职":
            active = [e for e in st.session_state.employees if e['status'] == '在职']
            if active:
                selected = st.selectbox("选择员工", [f"{e['name']} ({e['employee_id']})" for e in active])
                if st.button("办理离职"):
                    emp_id = selected.split('(')[-1].rstrip(')')
                    for emp in st.session_state.employees:
                        if emp['employee_id'] == emp_id:
                            emp['status'] = '离职'
                            emp['leave_date'] = datetime.now().strftime("%Y-%m-%d")
                            # 回收未归属股权
                            grants = [g for g in st.session_state.equity_grants 
                                     if g['employee_id'] == emp_id and g['status'] == '生效中']
                            unvested = sum(g['shares'] - g.get('vested_shares', 0) for g in grants)
                            if unvested > 0:
                                for g in grants:
                                    g['status'] = '已终止'
                                update_stock_pool(unvested, f"{emp['name']}离职回收", "离职回收")
                            break
                    st.success("已办理离职")
                    st.rerun()

# ========== 股权授予 ==========
def render_equity_grants():
    st.header("📈 股权授予管理")
    
    if st.session_state.equity_grants:
        # 准备展示数据
        display_data = []
        for grant in st.session_state.equity_grants:
            emp = find_employee(grant['employee_id'])
            row = grant.copy()
            row['员工姓名'] = emp['name'] if emp else '未知'
            row['部门'] = emp['department'] if emp else '未知'
            row['未归属股数'] = grant['shares'] - grant.get('vested_shares', 0)
            display_data.append(row)
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
        
        # 统计信息
        cols = st.columns(4)
        stats = [
            ("总授予数", len(df)),
            ("总授予股数", f"{df['shares'].sum():,}股"),
            ("已归属股数", f"{df['vested_shares'].sum():,}股"),
            ("未归属股数", f"{df['未归属股数'].sum():,}股")
        ]
        
        for col, (title, value) in zip(cols, stats):
            with col:
                st.metric(title, value)
        
        # 分析图表
        st.subheader("授予分析")
        col1, col2 = st.columns(2)
        
        with col1:
            dept_grants = df.groupby('部门')['shares'].sum().reset_index()
            fig = px.pie(dept_grants, values='shares', names='部门',
                        title="各部门授予分布")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无股权授予记录")

# ========== 动态监控 ==========
def render_monitoring():
    st.header("📈 动态监控")
    
    if st.session_state.operation_history:
        df = pd.DataFrame(st.session_state.operation_history)
        
        # 实时指标
        cols = st.columns(4)
        
        # 今日变动
        today = datetime.now().strftime("%Y-%m-%d")
        today_df = df[df['time'].str.startswith(today)]
        today_in = today_df[today_df['amount'] > 0]['amount'].sum()
        today_out = today_df[today_df['amount'] < 0]['amount'].sum()
        
        metrics = [
            ("今日变动", f"流入:{today_in:,}\n流出:{abs(today_out):,}", None),
            ("当前余额", f"{st.session_state.stock_pool_balance:,}股", None),
            ("使用率", 
             f"{(st.session_state.stock_pool_total-st.session_state.stock_pool_balance)/st.session_state.stock_pool_total*100:.1f}%" 
             if st.session_state.stock_pool_total > 0 else "0%",
             "⚠️" if st.session_state.stock_pool_balance/st.session_state.stock_pool_total < 0.2 else "✅"),
            ("操作总数", len(df), None)
        ]
        
        for col, (title, value, delta) in zip(cols, metrics):
            with col:
                st.metric(title, value, delta)
        
        st.markdown("---")
        
        # 操作历史
        st.subheader("操作历史")
        st.dataframe(df.sort_values('time', ascending=False), use_container_width=True)
        
        # 图表
        col1, col2 = st.columns(2)
        
        with col1:
            type_dist = df['type'].value_counts()
            fig1 = px.pie(values=type_dist.values, names=type_dist.index,
                         title="操作类型分布")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            df['time_dt'] = pd.to_datetime(df['time'])
            fig2 = px.line(df.sort_values('time_dt'), x='time_dt', y='balance',
                          title="股票池余额趋势")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("暂无操作历史")

# ========== 主标签页 ==========
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 仪表盘", "🎯 职级标准", "📋 HC规划", 
    "👥 员工管理", "📈 股权授予", "📈 动态监控"
])

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

# ========== 底部信息 ==========
st.markdown("---")
st.caption("🏢 股权激励动态管理Demo | 基于职级标准和HC规划的股权激励预算管理系统")

# ========== 运行应用 ==========
if __name__ == "__main__":
    pass
