import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json
import pickle

# 设置页面
st.set_page_config(
    page_title="股权激励动态管理Demo",
    page_icon="📈",
    layout="wide"
)

st.title("🏢 股权激励动态管理Demo")
st.markdown("---")

# 初始化session state
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

# 数据持久化函数
def save_data():
    """保存数据到文件"""
    try:
        data = {
            'level_standards': st.session_state.level_standards,
            'hc_plan': st.session_state.hc_plan,
            'employees': st.session_state.employees,
            'equity_grants': st.session_state.equity_grants,
            'stock_pool_balance': st.session_state.stock_pool_balance,
            'stock_pool_total': st.session_state.stock_pool_total,
            'operation_history': st.session_state.operation_history
        }
        with open('equity_data.pkl', 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        st.error(f"保存数据失败: {str(e)}")
        return False

def load_data():
    """从文件加载数据"""
    try:
        with open('equity_data.pkl', 'rb') as f:
            data = pickle.load(f)
            st.session_state.level_standards = data.get('level_standards', {})
            st.session_state.hc_plan = data.get('hc_plan', [])
            st.session_state.employees = data.get('employees', [])
            st.session_state.equity_grants = data.get('equity_grants', [])
            st.session_state.stock_pool_balance = data.get('stock_pool_balance', 0)
            st.session_state.stock_pool_total = data.get('stock_pool_total', 0)
            st.session_state.operation_history = data.get('operation_history', [])
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        return False

def export_data_json():
    """导出数据为JSON格式"""
    data = {
        'level_standards': st.session_state.level_standards,
        'hc_plan': st.session_state.hc_plan,
        'employees': st.session_state.employees,
        'equity_grants': st.session_state.equity_grants,
        'stock_pool_balance': st.session_state.stock_pool_balance,
        'stock_pool_total': st.session_state.stock_pool_total,
        'operation_history': st.session_state.operation_history,
        'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return json.dumps(data, indent=2, ensure_ascii=False)

def import_data_json(json_str):
    """从JSON导入数据"""
    try:
        data = json.loads(json_str)
        
        # 验证数据格式
        required_keys = ['level_standards', 'hc_plan', 'employees', 
                        'equity_grants', 'stock_pool_balance', 'stock_pool_total']
        
        if all(key in data for key in required_keys):
            st.session_state.level_standards = data['level_standards']
            st.session_state.hc_plan = data['hc_plan']
            st.session_state.employees = data['employees']
            st.session_state.equity_grants = data['equity_grants']
            st.session_state.stock_pool_balance = data['stock_pool_balance']
            st.session_state.stock_pool_total = data['stock_pool_total']
            st.session_state.operation_history = data.get('operation_history', [])
            return True
        else:
            st.error("导入的数据格式不正确")
            return False
    except Exception as e:
        st.error(f"导入数据失败: {str(e)}")
        return False

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
    
    # 数据持久化管理
    st.header("💾 数据管理")
    
    col_save, col_load = st.columns(2)
    with col_save:
        if st.button("保存数据到文件"):
            if save_data():
                st.success("数据已保存到文件！")
    
    with col_load:
        if st.button("从文件加载数据"):
            if load_data():
                st.success("数据已从文件加载！")
                st.rerun()
    
    # JSON导入导出
    st.subheader("JSON导入/导出")
    
    # 导出JSON
    if st.button("导出数据为JSON"):
        json_data = export_data_json()
        st.download_button(
            label="下载JSON文件",
            data=json_data,
            file_name=f"equity_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # 导入JSON
    uploaded_file = st.file_uploader("上传JSON文件", type=['json'])
    if uploaded_file is not None:
        try:
            json_str = uploaded_file.getvalue().decode("utf-8")
            if st.button("导入上传的JSON数据"):
                if import_data_json(json_str):
                    st.success("数据导入成功！")
                    st.rerun()
        except Exception as e:
            st.error(f"读取文件失败: {str(e)}")
    
    st.markdown("---")
    
    # 示例数据和重置
    st.header("📊 示例数据")
    
    if st.button("生成示例数据", type="primary"):
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
                'employee_id': f'E{str(i).zfill(3)}',
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
                        'grant_id': f'G{str(len(st.session_state.equity_grants) + 1).zfill(3)}',
                        'employee_id': employee['employee_id'],
                        'shares': grant_shares,
                        'grant_date': employee['join_date'],
                        'vesting_schedule': '4年匀速',
                        'vested_shares': int(grant_shares * np.random.uniform(0.1, 0.7)),
                        'status': '生效中'
                    })
        
        # 计算已使用股数
        used_shares = sum(grant['shares'] for grant in st.session_state.equity_grants)
        st.session_state.stock_pool_balance = options_pool_total - used_shares
        
        # 添加操作记录
        st.session_state.operation_history.append({
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': '生成示例',
            'description': '生成示例数据',
            'amount': 0,
            'balance': st.session_state.stock_pool_balance
        })
        
        st.success("示例数据生成完成！")
        st.rerun()
    
    if st.button("重置所有数据"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

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

def update_stock_pool(amount: int, description: str, change_type: str = "其他"):
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
        st.metric(
            "当前已使用",
            f"{current_usage:,} 股",
            delta=f"{current_usage/st.session_state.stock_pool_total*100 if st.session_state.stock_pool_total > 0 else 0:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "股票池余额",
            f"{st.session_state.stock_pool_balance:,} 股",
            delta=f"{st.session_state.stock_pool_balance/st.session_state.stock_pool_total*100 if st.session_state.stock_pool_total > 0 else 0:.1f}%"
        )
    
    with col4:
        available_rate = st.session_state.stock_pool_balance / total_required * 100 if total_required > 0 else 100
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
                '股数': [current_usage, st.session_state.stock_pool_balance],
                '颜色': ['#EF553B', '#00CC96']
            })
            
            fig1 = px.pie(
                pool_data,
                values='股数',
                names='状态',
                hole=0.5,
                color='状态',
                color_discrete_map={'已使用': '#EF553B', '未使用': '#00CC96'}
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
                dept = plan['department']
                level = plan['level']
                plan_count = plan['plan_count']
                
                if dept not in dept_data:
                    dept_data[dept] = {'requirement': 0, 'usage': 0}
                
                if level in st.session_state.level_standards:
                    dept_data[dept]['requirement'] += st.session_state.level_standards[level] * plan_count
            
            # 计算各部门当前使用
            for grant in st.session_state.equity_grants:
                employee_id = grant['employee_id']
                # 查找员工部门
                employee = next((emp for emp in st.session_state.employees if emp['employee_id'] == employee_id), None)
                if employee and employee['status'] == '在职':
                    dept = employee['department']
                    if dept in dept_data:
                        dept_data[dept]['usage'] += grant['shares']
            
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
            
            # 统计信息
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("职级数量", len(levels_df))
            with col_b:
                st.metric("最高标准", f"{levels_df['标准股数'].max():,}股")
            with col_c:
                st.metric("平均标准", f"{levels_df['标准股数'].mean():,.0f}股")
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
        
        if st.session_state.level_standards:
            # 选择要删除的职级
            delete_level = st.selectbox("选择要删除的职级", 
                                       [""] + list(st.session_state.level_standards.keys()))
            
            if delete_level and st.button("删除选定职级", type="secondary"):
                del st.session_state.level_standards[delete_level]
                st.success(f"已删除职级 {delete_level}")
                st.rerun()
            
            if st.button("清除所有标准"):
                st.session_state.level_standards = {}
                st.rerun()
    
    # 职级标准分析
    if st.session_state.level_standards:
        st.subheader("职级标准分析")
        
        # 将职级标准转换为DataFrame用于图表
        levels_data = []
        for level, shares in st.session_state.level_standards.items():
            levels_data.append({
                '职级': level,
                '标准股数': shares,
                '职级类型': '管理序列' if level.startswith('M') else '专业序列'
            })
        
        levels_df = pd.DataFrame(levels_data)
        
        # 创建图表
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                levels_df.sort_values('标准股数', ascending=False),
                x='职级',
                y='标准股数',
                color='职级类型',
                title="各职级标准股数对比",
                text_auto=True
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 职级类型分布
            type_summary = levels_df.groupby('职级类型')['标准股数'].sum().reset_index()
            fig2 = px.pie(
                type_summary,
                values='标准股数',
                names='职级类型',
                title="管理序列vs专业序列股数分布"
            )
            st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.header("📋 HC规划管理")
    
    # HC规划管理
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("HC规划列表")
        
        if st.session_state.hc_plan:
            hc_df = pd.DataFrame(st.session_state.hc_plan)
            
            # 计算每个规划的股数需求
            if st.session_state.level_standards:
                hc_df['单人员工股数'] = hc_df['level'].apply(
                    lambda x: st.session_state.level_standards.get(x, 0)
                )
                hc_df['总需求股数'] = hc_df['plan_count'] * hc_df['单人员工股数']
            
            st.dataframe(hc_df, use_container_width=True)
            
            # 汇总信息
            total_hc_count = hc_df['plan_count'].sum()
            total_hc_shares = hc_df['总需求股数'].sum() if '总需求股数' in hc_df.columns else 0
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("规划招聘人数", total_hc_count)
            with col_b:
                st.metric("规划总股数需求", f"{total_hc_shares:,}股")
        else:
            st.info("暂无HC规划数据")
    
    with col2:
        st.subheader("HC规划操作")
        
        operation = st.radio("选择操作", ["添加规划", "批量导入", "编辑规划"])
        
        if operation == "添加规划":
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
        
        elif operation == "批量导入":
            st.info("批量导入功能开发中...")
            # 这里可以添加CSV导入功能
            # uploaded_file = st.file_uploader("上传CSV文件", type=['csv'])
        
        elif operation == "编辑规划":
            if st.session_state.hc_plan:
                hc_options = [f"{plan['department']} - {plan['level']} ({plan['year']}年)" 
                            for plan in st.session_state.hc_plan]
                selected_plan_idx = st.selectbox("选择要编辑的规划", range(len(hc_options)), 
                                               format_func=lambda x: hc_options[x])
                
                if selected_plan_idx is not None:
                    plan = st.session_state.hc_plan[selected_plan_idx]
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        new_count = st.number_input("计划招聘人数", value=plan['plan_count'], min_value=1)
                    with col_b:
                        new_year = st.number_input("规划年度", value=plan['year'], min_value=2020, max_value=2030)
                    
                    if st.button("更新规划"):
                        st.session_state.hc_plan[selected_plan_idx]['plan_count'] = new_count
                        st.session_state.hc_plan[selected_plan_idx]['year'] = new_year
                        st.success("规划已更新")
                        st.rerun()
                    
                    if st.button("删除该规划", type="secondary"):
                        del st.session_state.hc_plan[selected_plan_idx]
                        st.success("规划已删除")
                        st.rerun()
        
        if st.session_state.hc_plan and st.button("清除所有规划", type="secondary"):
            st.session_state.hc_plan = []
            st.rerun()
    
    # HC规划分析
    if st.session_state.hc_plan:
        st.subheader("HC规划分析")
        
        hc_df = pd.DataFrame(st.session_state.hc_plan)
        if st.session_state.level_standards:
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
                color='department',
                text_auto=True
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            if '总需求股数' in dept_analysis.columns:
                fig2 = px.bar(
                    dept_analysis,
                    x='department',
                    y='总需求股数',
                    title="各部门规划股数需求",
                    color='department',
                    text_auto=True
                )
                st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.header("👥 员工管理")
    
    # 员工管理
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("员工列表")
        
        if st.session_state.employees:
            employees_df = pd.DataFrame(st.session_state.employees)
            
            # 添加搜索功能
            search_term = st.text_input("🔍 搜索员工（姓名、部门、职级）", "")
            if search_term:
                mask = employees_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
                employees_df = employees_df[mask]
            
            # 添加状态筛选
            status_filter = st.multiselect(
                "筛选状态",
                options=['在职', '拟入职', '离职'],
                default=['在职', '拟入职']
            )
            if status_filter:
                employees_df = employees_df[employees_df['status'].isin(status_filter)]
            
            st.dataframe(employees_df, use_container_width=True)
            
            # 员工统计
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                total_employees = len(employees_df)
                st.metric("筛选员工数", total_employees)
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
        grants_df = pd.DataFrame(st.session_state.equity_grants)
        
        # 关联员工信息
        employees_dict = {emp['employee_id']: emp for emp in st.session_state.employees}
        
        grants_display = []
        for grant in st.session_state.equity_grants:
            employee = employees_dict.get(grant['employee_id'], {})
            display_grant = grant.copy()
            display_grant['员工姓名'] = employee.get('name', '未知')
            display_grant['部门'] = employee.get('department', '未知')
            display_grant['职级'] = employee.get('level', '未知')
            display_grant['员工状态'] = employee.get('status', '未知')
            display_grant['未归属股数'] = grant['shares'] - grant.get('vested_shares', 0)
            grants_display.append(display_grant)
        
        grants_display_df = pd.DataFrame(grants_display)
        
        # 添加筛选功能
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            status_filter = st.multiselect(
                "筛选授予状态",
                options=grants_display_df['status'].unique(),
                default=['生效中']
            )
        with col_filter2:
            dept_filter = st.multiselect(
                "筛选部门",
                options=grants_display_df['部门'].unique()
            )
        
        # 应用筛选
        filtered_df = grants_display_df.copy()
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if dept_filter:
            filtered_df = filtered_df[filtered_df['部门'].isin(dept_filter)]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # 股权授予统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_grants = len(filtered_df)
            st.metric("总授予数", total_grants)
        
        with col2:
            total_shares = filtered_df['shares'].sum()
            st.metric("总授予股数", f"{total_shares:,}股")
        
        with col3:
            total_vested = filtered_df['vested_shares'].sum()
            st.metric("已归属股数", f"{total_vested:,}股")
        
        with col4:
            total_unvested = filtered_df['未归属股数'].sum()
            st.metric("未归属股数", f"{total_unvested:,}股")
        
        # 授予分析
        st.subheader("股权授予分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 按部门统计
            dept_grants = filtered_df.groupby('部门')['shares'].sum().reset_index()
            if not dept_grants.empty:
                fig1 = px.pie(
                    dept_grants,
                    values='shares',
                    names='部门',
                    title="各部门授予股数分布"
                )
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 按职级统计
            level_grants = filtered_df.groupby('职级')['shares'].sum().reset_index()
            if not level_grants.empty:
                fig2 = px.bar(
                    level_grants,
                    x='职级',
                    y='shares',
                    title="各职级授予股数",
                    color='职级',
                    text_auto=True
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        # 授予状态分析
        st.subheader("授予状态分析")
        
        status_summary = filtered_df.groupby('status').agg({
            'shares': 'sum',
            'grant_id': 'count'
        }).rename(columns={'shares': '总股数', 'grant_id': '授予数量'}).reset_index()
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            fig3 = px.bar(
                status_summary,
                x='status',
                y='总股数',
                title="按状态统计授予股数",
                color='status',
                text_auto=True
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col_b:
            fig4 = px.pie(
                status_summary,
                values='总股数',
                names='status',
                title="授予状态分布"
            )
            st.plotly_chart(fig4, use_container_width=True)
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
                color = "red"
            elif usage_rate > 70:
                status = "⚠️ 预警"
                color = "orange"
            else:
                status = "✅ 充足"
                color = "green"
            
            st.markdown(f"""
            <div style="text-align: center;">
                <h3 style="color: {color};">{status}</h3>
                <p>使用率: {usage_rate:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # 预测可持续月数
            hc_requirement = calculate_hc_requirement()
            monthly_requirement = hc_requirement / 12 if hc_requirement > 0 else 0
            
            if monthly_requirement > 0:
                months_supply = st.session_state.stock_pool_balance / monthly_requirement
            else:
                months_supply = 999
            
            if months_supply < 3:
                supply_status = "🚨 紧急"
            elif months_supply < 6:
                supply_status = "⚠️ 紧张"
            else:
                supply_status = "✅ 充足"
            
            st.metric(
                "预计可持续月数",
                f"{months_supply:.1f}个月",
                delta=supply_status,
                delta_color="normal" if months_supply > 6 else "inverse"
            )
        
        st.markdown("---")
        
        # 交易历史
        st.subheader("操作历史")
        
        # 添加操作类型筛选
        operation_types = history_df['type'].unique()
        selected_types = st.multiselect("筛选操作类型", operation_types, default=operation_types)
        
        if selected_types:
            filtered_history = history_df[history_df['type'].isin(selected_types)]
        else:
            filtered_history = history_df
        
        st.dataframe(
            filtered_history.sort_values('time', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # 可视化
        col1, col2 = st.columns(2)
        
        with col1:
            # 操作类型分布
            type_dist = filtered_history['type'].value_counts()
            if not type_dist.empty:
                fig1 = px.pie(
                    values=type_dist.values,
                    names=type_dist.index,
                    title="操作类型分布"
                )
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 余额变化趋势
            if not filtered_history.empty:
                filtered_history['time_dt'] = pd.to_datetime(filtered_history['time'])
                fig2 = px.line(
                    filtered_history.sort_values('time_dt'),
                    x='time_dt',
                    y='balance',
                    title="股票池余额变化趋势"
                )
                fig2.update_layout(xaxis_title="时间", yaxis_title="余额(股)")
                st.plotly_chart(fig2, use_container_width=True)
        
        # 操作频率分析
        st.subheader("操作频率分析")
        
        if not filtered_history.empty:
            filtered_history['date'] = pd.to_datetime(filtered_history['time']).dt.date
            daily_operations = filtered_history.groupby('date').size().reset_index(name='操作次数')
            
            fig3 = px.bar(
                daily_operations,
                x='date',
                y='操作次数',
                title="每日操作频率",
                color='操作次数'
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("暂无操作历史")

# 底部信息
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    <p>🏢 股权激励动态管理Demo | 基于职级标准和HC规划，动态管理股权激励占用</p>
    <p style="color: gray; font-size: 0.9em;">版本 1.0.0 | 最后更新: 2024年1月</p>
</div>
""", unsafe_allow_html=True)

# 运行应用
if __name__ == "__main__":
    # 自动加载上次保存的数据
    if load_data():
        st.sidebar.success("自动加载上次保存的数据完成")
