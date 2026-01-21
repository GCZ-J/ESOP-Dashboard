import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import io
import base64

# 页面配置
st.set_page_config(
    page_title="股权激励动态管理Demo",
    page_icon="📈",
    layout="wide"
)

st.title("🏢 股权激励动态管理Demo")
st.markdown("---")

# 初始化session state
def init_session_state():
    """初始化所有session state变量"""
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

# 辅助函数
def calculate_hc_requirement():
    """计算HC规划的总股数需求"""
    if not st.session_state.hc_plan or not st.session_state.level_standards:
        return 0
    
    total_required = 0
    for plan in st.session_state.hc_plan:
        level = plan.get('level')
        plan_count = plan.get('plan_count', 0)
        if level in st.session_state.level_standards:
            total_required += st.session_state.level_standards[level] * plan_count
    return total_required

def calculate_current_usage():
    """计算当前已使用的股数"""
    return sum(grant['shares'] for grant in st.session_state.equity_grants)

def update_stock_pool(amount, description, change_type="其他"):
    """更新股票池余额"""
    old_balance = st.session_state.stock_pool_balance
    new_balance = old_balance + amount
    
    st.session_state.stock_pool_balance = new_balance
    st.session_state.operation_history.append({
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': change_type,
        'description': description,
        'amount': amount,
        'balance': new_balance
    })
    
    return new_balance

def generate_sample_data():
    """生成示例数据"""
    np.random.seed(42)
    
    # 生成职级标准示例数据
    levels = ['P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'M1', 'M2', 'M3', 'M4']
    standard_shares = [10000, 20000, 40000, 80000, 150000, 250000, 400000, 50000, 100000, 200000, 300000]
    
    st.session_state.level_standards = dict(zip(levels, standard_shares))
    
    # 生成HC规划示例数据
    departments = ['研发部', '产品部', '市场部', '销售部', '职能部', '技术部']
    st.session_state.hc_plan = []
    
    for dept in departments:
        for level in ['P6', 'P7', 'P8', 'M1', 'M2']:
            st.session_state.hc_plan.append({
                'department': dept,
                'level': level,
                'plan_count': np.random.randint(1, 4),
                'year': 2024
            })
    
    # 生成员工示例数据
    st.session_state.employees = []
    for i in range(1, 31):
        dept = np.random.choice(departments)
        level = np.random.choice(['P6', 'P7', 'P8', 'M1', 'M2'])
        status = np.random.choice(['在职', '在职', '在职', '拟入职', '离职'], p=[0.7, 0.7, 0.7, 0.2, 0.1])
        
        employee = {
            'employee_id': f'E{i:03d}',
            'name': f'员工{i}',
            'department': dept,
            'level': level,
            'join_date': f'202{np.random.randint(2, 4)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 28):02d}',
            'status': status
        }
        
        if status == '离职':
            employee['leave_date'] = f'202{np.random.randint(3, 4)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 28):02d}'
        
        st.session_state.employees.append(employee)
        
        # 如果在职，生成股权授予记录
        if status == '在职' and np.random.random() > 0.3:
            grant_shares = st.session_state.level_standards.get(level, 0)
            if grant_shares > 0:
                st.session_state.equity_grants.append({
                    'grant_id': f'G{len(st.session_state.equity_grants) + 1:03d}',
                    'employee_id': employee['employee_id'],
                    'shares': grant_shares,
                    'grant_date': employee['join_date'],
                    'vesting_schedule': '4年匀速',
                    'vested_shares': int(grant_shares * np.random.uniform(0.1, 0.7)),
                    'status': '生效中'
                })
    
    # 更新股票池余额
    used_shares = sum(grant['shares'] for grant in st.session_state.equity_grants)
    st.session_state.stock_pool_balance = st.session_state.stock_pool_total - used_shares

# 模板下载功能
def get_download_link(df, filename, link_text):
    """生成CSV下载链接"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 公司基本信息
    col1, col2 = st.columns(2)
    with col1:
        total_shares = st.number_input(
            "公司总股本（万股）:",
            min_value=1000,
            max_value=1000000,
            value=10000,
            step=1000
        )
    
    with col2:
        options_pool_pct = st.slider(
            "期权池比例（%）:",
            min_value=5,
            max_value=25,
            value=15,
            step=1
        )
    
    # 计算股票池
    options_pool_total = int(total_shares * 10000 * options_pool_pct / 100)
    st.session_state.stock_pool_total = options_pool_total
    
    if st.button("初始化股票池", type="primary"):
        st.session_state.stock_pool_balance = options_pool_total
        st.session_state.operation_history.append({
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': '初始化',
            'description': f'初始化股票池，总额: {options_pool_total:,}股',
            'amount': options_pool_total,
            'balance': options_pool_total
        })
        st.success(f"股票池初始化完成！总额: {options_pool_total:,}股")
    
    st.info(f"""
    **股票池信息:**
    - 总股本: {total_shares:,}万股
    - 期权池比例: {options_pool_pct}%
    - 股票池总额: {options_pool_total:,}股
    - 当前余额: {st.session_state.stock_pool_balance:,}股
    - 使用率: {((options_pool_total - st.session_state.stock_pool_balance) / options_pool_total * 100) if options_pool_total > 0 else 0:.1f}%
    """)
    
    st.markdown("---")
    
    # 模板管理
    st.header("📁 模板管理")
    
    tab1, tab2 = st.tabs(["下载模板", "上传数据"])
    
    with tab1:
        st.subheader("下载模板")
        
        # 职级标准模板
        level_template = pd.DataFrame({
            '职级': ['P5', 'P6', 'P7', 'P8', 'M1', 'M2'],
            '标准股数': [10000, 20000, 40000, 80000, 50000, 100000]
        })
        st.markdown(get_download_link(level_template, "职级标准模板.csv", "📥 下载职级标准模板"), unsafe_allow_html=True)
        
        # HC规划模板
        hc_template = pd.DataFrame({
            'department': ['研发部', '产品部', '市场部'],
            'level': ['P7', 'P6', 'M1'],
            'plan_count': [2, 3, 1],
            'year': [2024, 2024, 2024]
        })
        st.markdown(get_download_link(hc_template, "HC规划模板.csv", "📥 下载HC规划模板"), unsafe_allow_html=True)
        
        # 员工数据模板
        employee_template = pd.DataFrame({
            'employee_id': ['E001', 'E002'],
            'name': ['张三', '李四'],
            'department': ['研发部', '产品部'],
            'level': ['P7', 'P6'],
            'join_date': ['2023-01-15', '2023-06-20'],
            'status': ['在职', '拟入职']
        })
        st.markdown(get_download_link(employee_template, "员工数据模板.csv", "📥 下载员工数据模板"), unsafe_allow_html=True)
        
        # 授予数据模板
        grant_template = pd.DataFrame({
            'grant_id': ['G001', 'G002'],
            'employee_id': ['E001', 'E002'],
            'shares': [20000, 15000],
            'grant_date': ['2023-01-15', '2023-06-20'],
            'vesting_schedule': ['4年匀速', '1年等待+3年匀速'],
            'vested_shares': [5000, 0],
            'status': ['生效中', '生效中']
        })
        st.markdown(get_download_link(grant_template, "股权授予模板.csv", "📥 下载股权授予模板"), unsafe_allow_html=True)
    
    with tab2:
        st.subheader("上传数据")
        
        upload_type = st.selectbox("选择上传数据类型", ["职级标准", "HC规划", "员工数据", "股权授予"])
        
        uploaded_file = st.file_uploader(f"上传{upload_type}数据 (CSV)", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                if upload_type == "职级标准":
                    if '职级' in df.columns and '标准股数' in df.columns:
                        st.session_state.level_standards = dict(zip(df['职级'], df['标准股数']))
                        st.success(f"成功导入 {len(df)} 条职级标准")
                    else:
                        st.error("CSV文件必须包含'职级'和'标准股数'列")
                
                elif upload_type == "HC规划":
                    required_cols = ['department', 'level', 'plan_count', 'year']
                    if all(col in df.columns for col in required_cols):
                        st.session_state.hc_plan = df.to_dict('records')
                        st.success(f"成功导入 {len(df)} 条HC规划")
                    else:
                        missing = [col for col in required_cols if col not in df.columns]
                        st.error(f"CSV文件缺少列: {', '.join(missing)}")
                
                elif upload_type == "员工数据":
                    required_cols = ['employee_id', 'name', 'department', 'level', 'join_date', 'status']
                    if all(col in df.columns for col in required_cols):
                        st.session_state.employees = df.to_dict('records')
                        st.success(f"成功导入 {len(df)} 条员工数据")
                    else:
                        missing = [col for col in required_cols if col not in df.columns]
                        st.error(f"CSV文件缺少列: {', '.join(missing)}")
                
                elif upload_type == "股权授予":
                    required_cols = ['grant_id', 'employee_id', 'shares', 'grant_date', 'vesting_schedule', 'vested_shares', 'status']
                    if all(col in df.columns for col in required_cols):
                        st.session_state.equity_grants = df.to_dict('records')
                        
                        # 更新股票池余额
                        used_shares = sum(grant['shares'] for grant in st.session_state.equity_grants)
                        st.session_state.stock_pool_balance = st.session_state.stock_pool_total - used_shares
                        
                        st.success(f"成功导入 {len(df)} 条股权授予记录")
                    else:
                        missing = [col for col in required_cols if col not in df.columns]
                        st.error(f"CSV文件缺少列: {', '.join(missing)}")
                
                st.dataframe(df.head(), use_container_width=True)
                
            except Exception as e:
                st.error(f"文件读取失败: {str(e)}")
    
    st.markdown("---")
    
    # 系统管理
    st.header("⚡ 系统管理")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("生成示例数据"):
            generate_sample_data()
            st.success("示例数据生成完成！")
            st.rerun()
    
    with col2:
        if st.button("重置所有数据"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            st.rerun()

# 主标签页
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 仪表盘", 
    "🎯 职级标准", 
    "📋 HC规划", 
    "👥 员工管理", 
    "📈 股权授予", 
    "📈 动态监控"
])

with tab1:
    st.header("📊 股权激励管理仪表盘")
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_required = calculate_hc_requirement()
        st.metric(
            "HC规划需求",
            f"{total_required:,} 股",
            help="基于HC规划和职级标准计算的总需求"
        )
    
    with col2:
        current_usage = calculate_current_usage()
        usage_rate = (current_usage / st.session_state.stock_pool_total * 100) if st.session_state.stock_pool_total > 0 else 0
        st.metric(
            "当前已使用",
            f"{current_usage:,} 股",
            delta=f"{usage_rate:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "股票池余额",
            f"{st.session_state.stock_pool_balance:,} 股",
            delta=f"{st.session_state.stock_pool_balance/st.session_state.stock_pool_total*100 if st.session_state.stock_pool_total > 0 else 0:.1f}%"
        )
    
    with col4:
        available_rate = (st.session_state.stock_pool_balance / total_required * 100) if total_required > 0 else 100
        st.metric(
            "可用比例",
            f"{available_rate:.1f}%",
            delta=f"剩余 {st.session_state.stock_pool_balance:,} 股",
            delta_color="normal" if available_rate > 20 else "inverse"
        )
    
    st.markdown("---")
    
    # 可视化图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("股票池构成")
        
        if st.session_state.stock_pool_total > 0:
            pool_data = pd.DataFrame({
                '状态': ['已使用', '未使用'],
                '股数': [current_usage, st.session_state.stock_pool_balance]
            })
            
            fig1 = px.pie(
                pool_data,
                values='股数',
                names='状态',
                hole=0.5,
                color_discrete_sequence=['#EF553B', '#00CC96']
            )
            fig1.update_traces(textinfo='percent+label+value')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("请先初始化股票池")
    
    with col2:
        st.subheader("HC需求 vs 当前使用")
        
        if st.session_state.hc_plan and st.session_state.level_standards:
            # 按部门计算需求和使用
            dept_data = {}
            
            # 计算各部门HC需求
            for plan in st.session_state.hc_plan:
                dept = plan.get('department')
                level = plan.get('level')
                plan_count = plan.get('plan_count')
                
                if dept not in dept_data:
                    dept_data[dept] = {'requirement': 0, 'usage': 0}
                
                if level in st.session_state.level_standards:
                    dept_data[dept]['requirement'] += st.session_state.level_standards[level] * plan_count
            
            # 计算各部门当前使用
            for grant in st.session_state.equity_grants:
                # 查找员工
                employee = next((emp for emp in st.session_state.employees 
                               if emp['employee_id'] == grant['employee_id'] and emp['status'] == '在职'), None)
                if employee and employee.get('department') in dept_data:
                    dept_data[employee['department']]['usage'] += grant['shares']
            
            # 准备图表数据
            dept_list = list(dept_data.keys())
            requirement_values = [dept_data[dept]['requirement'] for dept in dept_list]
            usage_values = [dept_data[dept]['usage'] for dept in dept_list]
            
            fig2 = go.Figure(data=[
                go.Bar(name='HC需求', x=dept_list, y=requirement_values, marker_color='#636efa'),
                go.Bar(name='当前使用', x=dept_list, y=usage_values, marker_color='#ef553b')
            ])
            
            fig2.update_layout(
                title="各部门HC需求与当前使用对比",
                barmode='group',
                xaxis_title="部门",
                yaxis_title="股数"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("请先设置职级标准和HC规划")
    
    # 预警信息
    st.subheader("⚠️ 预警信息")
    
    warnings = []
    
    # 检查股票池是否充足
    if total_required > st.session_state.stock_pool_total:
        warnings.append(f"⚠️ HC规划需求({total_required:,}股)超过股票池总额({st.session_state.stock_pool_total:,}股)")
    
    if st.session_state.stock_pool_balance < total_required * 0.2:
        warnings.append(f"⚠️ 股票池余额({st.session_state.stock_pool_balance:,}股)不足HC规划需求的20%")
    
    # 检查未处理的拟入职员工
    pending_joins = [emp for emp in st.session_state.employees if emp['status'] == '拟入职']
    if pending_joins:
        warnings.append(f"⚠️ 有{len(pending_joins)}名拟入职员工待处理")
    
    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("✅ 所有指标正常")

with tab2:
    st.header("🎯 职级标准设置")
    
    # 职级标准管理
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("当前职级标准")
        
        if st.session_state.level_standards:
            levels_df = pd.DataFrame(
                list(st.session_state.level_standards.items()),
                columns=['职级', '标准股数']
            )
            st.dataframe(levels_df, use_container_width=True)
        else:
            st.info("暂无职级标准数据")
    
    with col2:
        st.subheader("添加/修改职级标准")
        
        with st.form("level_standard_form"):
            level = st.text_input("职级", placeholder="如: P7, M2")
            standard_shares = st.number_input("标准股数", min_value=0, value=20000, step=1000)
            
            if st.form_submit_button("保存标准"):
                if level and standard_shares > 0:
                    st.session_state.level_standards[level] = standard_shares
                    st.success(f"已设置职级 {level} 的标准股数为 {standard_shares:,}股")
                    st.rerun()
                else:
                    st.error("请输入有效的职级和股数")
        
        if st.session_state.level_standards and st.button("清除所有标准"):
            st.session_state.level_standards = {}
            st.rerun()
    
    # 职级标准分析
    if st.session_state.level_standards:
        st.subheader("职级标准分析")
        
        levels_data = []
        for level, shares in st.session_state.level_standards.items():
            levels_data.append({
                '职级': level,
                '标准股数': shares,
                '职级类型': '管理序列' if level.startswith('M') else '专业序列'
            })
        
        levels_df = pd.DataFrame(levels_data)
        
        fig = px.bar(
            levels_df.sort_values('标准股数', ascending=False),
            x='职级',
            y='标准股数',
            color='职级类型',
            title="各职级标准股数对比"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("📋 HC规划管理")
    
    # HC规划管理
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("HC规划列表")
        
        if st.session_state.hc_plan:
            hc_df = pd.DataFrame(st.session_state.hc_plan)
            
            # 计算每个规划的股数需求
            hc_df['单人员工股数'] = hc_df['level'].apply(
                lambda x: st.session_state.level_standards.get(x, 0)
            )
            hc_df['总需求股数'] = hc_df['plan_count'] * hc_df['单人员工股数']
            
            st.dataframe(hc_df, use_container_width=True)
            
            # 汇总信息
            total_hc_count = hc_df['plan_count'].sum()
            total_hc_shares = hc_df['总需求股数'].sum()
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("规划招聘人数", total_hc_count)
            with col_b:
                st.metric("规划总股数需求", f"{total_hc_shares:,}股")
        else:
            st.info("暂无HC规划数据")
    
    with col2:
        st.subheader("添加HC规划")
        
        with st.form("hc_plan_form"):
            department = st.text_input("部门", placeholder="如: 研发部")
            
            # 获取已设置的职级
            if st.session_state.level_standards:
                available_levels = list(st.session_state.level_standards.keys())
                level = st.selectbox("职级", available_levels)
            else:
                st.warning("请先设置职级标准")
                level = st.text_input("职级（需手动输入）", placeholder="如: P7")
            
            plan_count = st.number_input("计划招聘人数", min_value=1, value=1, step=1)
            year = st.number_input("规划年度", min_value=2020, max_value=2030, value=2024)
            
            if st.form_submit_button("添加规划"):
                if department and level and plan_count > 0:
                    new_plan = {
                        'department': department,
                        'level': level,
                        'plan_count': plan_count,
                        'year': year
                    }
                    
                    # 检查是否已存在相同部门和职级的规划
                    existing_idx = -1
                    for i, plan in enumerate(st.session_state.hc_plan):
                        if (plan['department'] == department and 
                            plan['level'] == level and 
                            plan['year'] == year):
                            existing_idx = i
                            break
                    
                    if existing_idx >= 0:
                        st.session_state.hc_plan[existing_idx] = new_plan
                        st.success(f"已更新{department} {level}的HC规划")
                    else:
                        st.session_state.hc_plan.append(new_plan)
                        st.success(f"已添加{department} {level}的HC规划")
                    
                    st.rerun()
                else:
                    st.error("请填写完整的规划信息")
        
        if st.session_state.hc_plan and st.button("清除所有规划"):
            st.session_state.hc_plan = []
            st.rerun()
    
    # HC规划分析
    if st.session_state.hc_plan:
        st.subheader("HC规划分析")
        
        hc_df = pd.DataFrame(st.session_state.hc_plan)
        hc_df['单人员工股数'] = hc_df['level'].apply(
            lambda x: st.session_state.level_standards.get(x, 0)
        )
        hc_df['总需求股数'] = hc_df['plan_count'] * hc_df['单人员工股数']
        
        # 按部门分析
        dept_analysis = hc_df.groupby('department').agg({
            'plan_count': 'sum',
            '总需求股数': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                dept_analysis,
                x='department',
                y='plan_count',
                title="各部门规划招聘人数",
                color='department'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(
                dept_analysis,
                x='department',
                y='总需求股数',
                title="各部门规划股数需求",
                color='department'
            )
            st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.header("👥 员工管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("员工列表")
        
        if st.session_state.employees:
            employees_df = pd.DataFrame(st.session_state.employees)
            st.dataframe(employees_df, use_container_width=True)
            
            # 员工统计
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                total_employees = len(employees_df)
                st.metric("员工总数", total_employees)
            with col_b:
                active_employees = len(employees_df[employees_df['status'] == '在职'])
                st.metric("在职员工", active_employees)
            with col_c:
                pending_employees = len(employees_df[employees_df['status'] == '拟入职'])
                st.metric("拟入职员工", pending_employees)
        else:
            st.info("暂无员工数据")
    
    with col2:
        st.subheader("员工操作")
        
        operation = st.radio(
            "选择操作",
            ["新增员工", "办理入职", "办理离职", "办理晋升"]
        )
        
        if operation == "新增员工":
            with st.form("add_employee_form"):
                name = st.text_input("姓名", placeholder="如: 张三")
                department = st.text_input("部门", placeholder="如: 研发部")
                
                if st.session_state.level_standards:
                    available_levels = list(st.session_state.level_standards.keys())
                    level = st.selectbox("职级", available_levels)
                else:
                    level = st.text_input("职级", placeholder="如: P7")
                
                join_date = st.date_input("入职日期", value=datetime.now())
                status = st.selectbox("状态", ["拟入职", "在职"])
                
                if st.form_submit_button("添加员工"):
                    if name and department and level:
                        # 生成员工ID
                        employee_id = f"E{len(st.session_state.employees) + 1:03d}"
                        
                        new_employee = {
                            'employee_id': employee_id,
                            'name': name,
                            'department': department,
                            'level': level,
                            'join_date': join_date.strftime("%Y-%m-%d"),
                            'status': status
                        }
                        
                        st.session_state.employees.append(new_employee)
                        st.success(f"已添加员工: {name} ({employee_id})")
                        
                        # 如果是直接入职状态，自动授予股权
                        if status == '在职' and level in st.session_state.level_standards:
                            standard_shares = st.session_state.level_standards[level]
                            
                            # 检查股票池余额
                            if standard_shares <= st.session_state.stock_pool_balance:
                                grant_id = f"G{len(st.session_state.equity_grants) + 1:03d}"
                                
                                st.session_state.equity_grants.append({
                                    'grant_id': grant_id,
                                    'employee_id': employee_id,
                                    'shares': standard_shares,
                                    'grant_date': join_date.strftime("%Y-%m-%d"),
                                    'vesting_schedule': '4年匀速',
                                    'vested_shares': 0,
                                    'status': '生效中'
                                })
                                
                                # 更新股票池
                                new_balance = update_stock_pool(
                                    -standard_shares,
                                    f"员工{name}({employee_id})入职授予股权",
                                    "入职授予"
                                )
                                
                                st.success(f"已自动授予{standard_shares:,}股，股票池余额: {new_balance:,}股")
                            else:
                                st.warning(f"股票池余额不足，无法自动授予股权（需{standard_shares:,}股，余{st.session_state.stock_pool_balance:,}股）")
                        
                        st.rerun()
                    else:
                        st.error("请填写完整的员工信息")
        
        elif operation == "办理入职":
            # 筛选拟入职员工
            pending_employees = [emp for emp in st.session_state.employees if emp['status'] == '拟入职']
            
            if pending_employees:
                employee_options = {f"{emp['name']} ({emp['employee_id']})": emp for emp in pending_employees}
                selected_key = st.selectbox("选择拟入职员工", list(employee_options.keys()))
                
                if selected_key:
                    selected_employee = employee_options[selected_key]
                    
                    st.info(f"""
                    **员工信息:**
                    - 姓名: {selected_employee['name']}
                    - 部门: {selected_employee['department']}
                    - 职级: {selected_employee['level']}
                    """)
                    
                    if st.button("办理入职"):
                        # 更新员工状态
                        for emp in st.session_state.employees:
                            if emp['employee_id'] == selected_employee['employee_id']:
                                emp['status'] = '在职'
                                emp['join_date'] = datetime.now().strftime("%Y-%m-%d")
                                break
                        
                        # 授予股权
                        level = selected_employee['level']
                        if level in st.session_state.level_standards:
                            standard_shares = st.session_state.level_standards[level]
                            
                            # 检查股票池余额
                            if standard_shares <= st.session_state.stock_pool_balance:
                                grant_id = f"G{len(st.session_state.equity_grants) + 1:03d}"
                                
                                st.session_state.equity_grants.append({
                                    'grant_id': grant_id,
                                    'employee_id': selected_employee['employee_id'],
                                    'shares': standard_shares,
                                    'grant_date': datetime.now().strftime("%Y-%m-%d"),
                                    'vesting_schedule': '4年匀速',
                                    'vested_shares': 0,
                                    'status': '生效中'
                                })
                                
                                # 更新股票池
                                new_balance = update_stock_pool(
                                    -standard_shares,
                                    f"员工{selected_employee['name']}({selected_employee['employee_id']})入职授予股权",
                                    "入职授予"
                                )
                                
                                st.success(f"已办理入职并授予{standard_shares:,}股，股票池余额: {new_balance:,}股")
                                st.rerun()
                            else:
                                st.error(f"股票池余额不足，无法授予股权（需{standard_shares:,}股，余{st.session_state.stock_pool_balance:,}股）")
                        else:
                            st.error(f"职级{level}的标准股数未设置")
            else:
                st.info("暂无拟入职员工")
        
        elif operation == "办理离职":
            # 筛选在职员工
            active_employees = [emp for emp in st.session_state.employees if emp['status'] == '在职']
            
            if active_employees:
                employee_options = {f"{emp['name']} ({emp['employee_id']})": emp for emp in active_employees}
                selected_key = st.selectbox("选择离职员工", list(employee_options.keys()))
                
                if selected_key:
                    selected_employee = employee_options[selected_key]
                    
                    st.info(f"""
                    **员工信息:**
                    - 姓名: {selected_employee['name']}
                    - 部门: {selected_employee['department']}
                    - 职级: {selected_employee['level']}
                    """)
                    
                    leave_date = st.date_input("离职日期", value=datetime.now())
                    leave_reason = st.selectbox("离职原因", ["个人发展", "家庭原因", "退休", "合同到期", "协商解除", "其他"])
                    
                    if st.button("办理离职"):
                        # 更新员工状态
                        for emp in st.session_state.employees:
                            if emp['employee_id'] == selected_employee['employee_id']:
                                emp['status'] = '离职'
                                emp['leave_date'] = leave_date.strftime("%Y-%m-%d")
                                emp['leave_reason'] = leave_reason
                                break
                        
                        # 回收未归属股权
                        employee_grants = [g for g in st.session_state.equity_grants 
                                         if g['employee_id'] == selected_employee['employee_id'] and g['status'] == '生效中']
                        
                        total_unvested = 0
                        for grant in employee_grants:
                            unvested_shares = grant['shares'] - grant.get('vested_shares', 0)
                            total_unvested += unvested_shares
                            
                            # 更新授予状态
                            grant['status'] = '已终止'
                        
                        if total_unvested > 0:
                            # 回收股权到股票池
                            new_balance = update_stock_pool(
                                total_unvested,
                                f"员工{selected_employee['name']}({selected_employee['employee_id']})离职回收股权",
                                "离职回收"
                            )
                            
                            st.success(f"已办理离职，回收{total_unvested:,}股未归属股权，股票池余额: {new_balance:,}股")
                        else:
                            st.success("已办理离职")
                        
                        st.rerun()
            else:
                st.info("暂无在职员工")
        
        elif operation == "办理晋升":
            # 筛选在职员工
            active_employees = [emp for emp in st.session_state.employees if emp['status'] == '在职']
            
            if active_employees:
                employee_options = {f"{emp['name']} ({emp['employee_id']}) - 当前: {emp['level']}": emp for emp in active_employees}
                selected_key = st.selectbox("选择晋升员工", list(employee_options.keys()))
                
                if selected_key:
                    selected_employee = employee_options[selected_key]
                    current_level = selected_employee['level']
                    
                    st.info(f"""
                    **员工信息:**
                    - 姓名: {selected_employee['name']}
                    - 部门: {selected_employee['department']}
                    - 当前职级: {current_level}
                    - 当前标准股数: {st.session_state.level_standards.get(current_level, 0):,}股
                    """)
                    
                    # 选择新职级
                    if st.session_state.level_standards:
                        available_levels = [l for l in st.session_state.level_standards.keys() if l != current_level]
                        new_level = st.selectbox("晋升至职级", available_levels)
                        
                        if new_level:
                            current_standard = st.session_state.level_standards.get(current_level, 0)
                            new_standard = st.session_state.level_standards.get(new_level, 0)
                            
                            if new_standard > current_standard:
                                additional_shares = new_standard - current_standard
                                
                                st.warning(f"""
                                **晋升将增加股权授予:**
                                - 当前标准: {current_standard:,}股
                                - 新标准: {new_standard:,}股
                                - 需补授予: {additional_shares:,}股
                                """)
                                
                                if st.button("办理晋升"):
                                    # 更新员工职级
                                    for emp in st.session_state.employees:
                                        if emp['employee_id'] == selected_employee['employee_id']:
                                            emp['level'] = new_level
                                            break
                                    
                                    # 补授予股权
                                    if additional_shares <= st.session_state.stock_pool_balance:
                                        grant_id = f"G{len(st.session_state.equity_grants) + 1:03d}"
                                        
                                        st.session_state.equity_grants.append({
                                            'grant_id': grant_id,
                                            'employee_id': selected_employee['employee_id'],
                                            'shares': additional_shares,
                                            'grant_date': datetime.now().strftime("%Y-%m-%d"),
                                            'vesting_schedule': '4年匀速',
                                            'vested_shares': 0,
                                            'status': '生效中',
                                            'type': '晋升补授予'
                                        })
                                        
                                        # 更新股票池
                                        new_balance = update_stock_pool(
                                            -additional_shares,
                                            f"员工{selected_employee['name']}({selected_employee['employee_id']})晋升补授予股权",
                                            "晋升授予"
                                        )
                                        
                                        st.success(f"已办理晋升并补授予{additional_shares:,}股，股票池余额: {new_balance:,}股")
                                        st.rerun()
                                    else:
                                        st.error(f"股票池余额不足，无法补授予股权（需{additional_shares:,}股，余{st.session_state.stock_pool_balance:,}股）")
                            elif new_standard == current_standard:
                                st.info("新旧职级标准相同，无需调整股权")
                                
                                if st.button("仅更新职级"):
                                    for emp in st.session_state.employees:
                                        if emp['employee_id'] == selected_employee['employee_id']:
                                            emp['level'] = new_level
                                            break
                                    st.success("已更新职级")
                                    st.rerun()
                            else:
                                st.info("新职级标准较低，无需补授予股权")
                                
                                if st.button("更新职级"):
                                    for emp in st.session_state.employees:
                                        if emp['employee_id'] == selected_employee['employee_id']:
                                            emp['level'] = new_level
                                            break
                                    st.success("已更新职级")
                                    st.rerun()
            else:
                st.info("暂无在职员工")

with tab5:
    st.header("📈 股权授予管理")
    
    if st.session_state.equity_grants:
        # 关联员工信息
        employees_dict = {emp['employee_id']: emp for emp in st.session_state.employees}
        
        grants_display = []
        for grant in st.session_state.equity_grants:
            employee = employees_dict.get(grant['employee_id'], {})
            display_grant = grant.copy()
            display_grant['员工姓名'] = employee.get('name', '未知')
            display_grant['部门'] = employee.get('department', '未知')
            display_grant['职级'] = employee.get('level', '未知')
            display_grant['未归属股数'] = grant['shares'] - grant.get('vested_shares', 0)
            grants_display.append(display_grant)
        
        grants_display_df = pd.DataFrame(grants_display)
        
        st.dataframe(grants_display_df, use_container_width=True)
        
        # 股权授予统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_grants = len(grants_display_df)
            st.metric("总授予数", total_grants)
        
        with col2:
            total_shares = grants_display_df['shares'].sum()
            st.metric("总授予股数", f"{total_shares:,}股")
        
        with col3:
            total_vested = grants_display_df['vested_shares'].sum()
            st.metric("已归属股数", f"{total_vested:,}股")
        
        with col4:
            total_unvested = grants_display_df['未归属股数'].sum()
            st.metric("未归属股数", f"{total_unvested:,}股")
        
        # 授予分析
        st.subheader("股权授予分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 按部门统计
            dept_grants = grants_display_df.groupby('部门')['shares'].sum().reset_index()
            fig1 = px.pie(
                dept_grants,
                values='shares',
                names='部门',
                title="各部门授予股数分布"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 按职级统计
            level_grants = grants_display_df.groupby('职级')['shares'].sum().reset_index()
            fig2 = px.bar(
                level_grants,
                x='职级',
                y='shares',
                title="各职级授予股数",
                color='职级'
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("暂无股权授予记录")

with tab6:
    st.header("📈 动态监控")
    
    if st.session_state.operation_history:
        history_df = pd.DataFrame(st.session_state.operation_history)
        
        # 实时监控面板
        st.subheader("实时监控面板")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # 今日变动
            today = datetime.now().strftime("%Y-%m-%d")
            today_changes = history_df[history_df['time'].str.startswith(today)]
            
            if not today_changes.empty:
                today_in = today_changes[today_changes['amount'] > 0]['amount'].sum()
                today_out = today_changes[today_changes['amount'] < 0]['amount'].sum()
            else:
                today_in = today_out = 0
            
            st.metric("今日流入", f"{today_in:,}", delta=f"流出: {abs(today_out):,}")
        
        with col2:
            # 最近7天变动
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            recent_changes = history_df[history_df['time'] >= week_ago]
            
            if not recent_changes.empty:
                week_in = recent_changes[recent_changes['amount'] > 0]['amount'].sum()
                week_out = recent_changes[recent_changes['amount'] < 0]['amount'].sum()
            else:
                week_in = week_out = 0
            
            st.metric("本周净变化", f"{week_in + week_out:,}", 
                     delta=f"流入: {week_in:,} 流出: {abs(week_out):,}")
        
        with col3:
            # 当前使用率
            usage_rate = (st.session_state.stock_pool_total - st.session_state.stock_pool_balance) / st.session_state.stock_pool_total * 100 if st.session_state.stock_pool_total > 0 else 0
            
            if usage_rate > 90:
                status = "🚨 紧张"
            elif usage_rate > 70:
                status = "⚠️ 预警"
            else:
                status = "✅ 充足"
            
            st.metric(
                "股票池状态", 
                status,
                delta=f"使用率: {usage_rate:.1f}%"
            )
        
        with col4:
            # 预测可持续月数
            hc_requirement = calculate_hc_requirement()
            monthly_requirement = hc_requirement / 12 if hc_requirement > 0 else 0
            
            if monthly_requirement > 0:
                months_supply = st.session_state.stock_pool_balance / monthly_requirement
            else:
                months_supply = 999
            
            st.metric(
                "预计可持续月数",
                f"{months_supply:.1f}个月",
                delta_color="normal" if months_supply > 6 else "inverse"
            )
        
        st.markdown("---")
        
        # 交易历史
        st.subheader("操作历史")
        st.dataframe(
            history_df.sort_values('time', ascending=False),
            use_container_width=True
        )
        
        # 可视化
        col1, col2 = st.columns(2)
        
        with col1:
            # 操作类型分布
            type_dist = history_df['type'].value_counts()
            fig1 = px.pie(
                values=type_dist.values,
                names=type_dist.index,
                title="操作类型分布"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 余额变化趋势
            history_df['time_dt'] = pd.to_datetime(history_df['time'])
            fig2 = px.line(
                history_df.sort_values('time_dt'),
                x='time_dt',
                y='balance',
                title="股票池余额变化趋势"
            )
            fig2.update_layout(xaxis_title="时间", yaxis_title="余额(股)")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("暂无操作历史")

# 底部信息
st.markdown("---")
st.caption("🏢 股权激励动态管理Demo | 基于职级标准和HC规划，动态管理股权激励占用")

# 运行应用
if __name__ == "__main__":
    pass
