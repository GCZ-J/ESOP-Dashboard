import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 设置页面
st.set_page_config(page_title="股权激励管理", layout="wide")

st.title("🏢 股权激励年度股票池管理")
st.markdown("基于员工职级标准和人员异动动态管理股权激励预算池")
st.markdown("---")

# 初始化数据
if 'level_standards' not in st.session_state:
    st.session_state.level_standards = {
        'P5': 10000, 'P6': 20000, 'P7': 40000, 'P8': 80000,
        'M1': 50000, 'M2': 100000
    }
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'stock_pool' not in st.session_state:
    st.session_state.stock_pool = 5000000  # 500万股

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 股票池设置
    col1, col2 = st.columns(2)
    with col1:
        pool_total = st.number_input("股票池(万股)", 100, 10000, 500, 50)
    with col2:
        if st.button("设置"):
            st.session_state.stock_pool = pool_total * 10000
            st.success(f"设置成功: {pool_total:,}万股")
    
    st.markdown("---")
    
    # 一键生成数据
    if st.button("🚀 一键生成示例数据"):
        departments = ['研发部', '产品部', '市场部', '销售部']
        st.session_state.employees = []
        
        for i in range(1, 16):
            st.session_state.employees.append({
                '工号': f'E{i:03d}',
                '姓名': f'员工{i}',
                '部门': np.random.choice(departments),
                '职级': np.random.choice(['P6', 'P7', 'P8']),
                '状态': '在职'
            })
        
        st.success("✅ 示例数据已生成！")
        st.rerun()
    
    st.markdown("---")
    
    # 当前状态
    total_shares = 0
    for emp in st.session_state.employees:
        if emp.get('状态') == '在职':
            level = emp.get('职级', '')
            total_shares += st.session_state.level_standards.get(level, 0)
    
    usage_rate = (total_shares / st.session_state.stock_pool * 100) if st.session_state.stock_pool > 0 else 0
    
    st.info(f"""
    **📊 当前状态:**
    - 股票池: {st.session_state.stock_pool:,}股
    - 已使用: {total_shares:,}股
    - 使用率: {usage_rate:.1f}%
    - 员工数: {len(st.session_state.employees)}
    """)

# 主界面
tab1, tab2, tab3 = st.tabs(["📈 仪表盘", "👥 员工管理", "⚙️ 职级标准"])

with tab1:
    st.header("📈 股权激励预算池仪表盘")
    
    # 计算指标
    total_shares = 0
    dept_shares = {}
    level_shares = {}
    
    for emp in st.session_state.employees:
        if emp.get('状态') == '在职':
            level = emp.get('职级', '')
            shares = st.session_state.level_standards.get(level, 0)
            total_shares += shares
            
            # 按部门统计
            dept = emp.get('部门', '未分配')
            dept_shares[dept] = dept_shares.get(dept, 0) + shares
            
            # 按职级统计
            level_shares[level] = level_shares.get(level, 0) + shares
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("在职员工", len([e for e in st.session_state.employees if e.get('状态') == '在职']))
    with col2:
        st.metric("总需求", f"{total_shares:,}股")
    with col3:
        usage_rate = (total_shares / st.session_state.stock_pool * 100) if st.session_state.stock_pool > 0 else 0
        st.metric("使用率", f"{usage_rate:.1f}%")
    with col4:
        st.metric("剩余额度", f"{st.session_state.stock_pool - total_shares:,}股")
    
    # 进度条
    st.progress(min(usage_rate/100, 1.0))
    
    # 预警
    if usage_rate > 80:
        st.warning(f"⚠️ 股票池使用率较高 ({usage_rate:.1f}%)")
    elif usage_rate > 90:
        st.error(f"🚨 股票池使用率过高 ({usage_rate:.1f}%)")
    else:
        st.success(f"✅ 股票池使用正常")
    
    st.markdown("---")
    
    # 可视化
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 按部门分布")
        if dept_shares:
            dept_df = pd.DataFrame({
                '部门': list(dept_shares.keys()),
                '股数': list(dept_shares.values())
            })
            st.bar_chart(dept_df.set_index('部门'))
    
    with col2:
        st.subheader("📊 按职级分布")
        if level_shares:
            level_df = pd.DataFrame({
                '职级': list(level_shares.keys()),
                '股数': list(level_shares.values())
            })
            st.bar_chart(level_df.set_index('职级'))

with tab2:
    st.header("👥 员工管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("员工列表")
        if st.session_state.employees:
            # 计算每人股数
            display_data = []
            for emp in st.session_state.employees:
                emp_display = emp.copy()
                if emp.get('状态') == '在职':
                    level = emp.get('职级', '')
                    emp_display['年度股数'] = st.session_state.level_standards.get(level, 0)
                else:
                    emp_display['年度股数'] = 0
                display_data.append(emp_display)
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无员工数据，请先生成示例数据")
    
    with col2:
        st.subheader("员工操作")
        
        operation = st.radio("选择操作", ["新增员工", "办理离职", "办理晋升"])
        
        if operation == "新增员工":
            with st.form("add_form"):
                name = st.text_input("姓名")
                department = st.selectbox("部门", ["研发部", "产品部", "市场部", "销售部", "人力资源部"])
                level = st.selectbox("职级", list(st.session_state.level_standards.keys()))
                
                if st.form_submit_button("添加"):
                    if name:
                        new_id = f'E{len(st.session_state.employees) + 1:03d}'
                        st.session_state.employees.append({
                            '工号': new_id,
                            '姓名': name,
                            '部门': department,
                            '职级': level,
                            '状态': '在职'
                        })
                        st.success(f"已添加: {name}")
                        st.rerun()
        
        elif operation == "办理离职":
            if st.session_state.employees:
                active_emps = [e for e in st.session_state.employees if e.get('状态') == '在职']
                if active_emps:
                    options = {f"{e['姓名']} ({e['工号']})": e for e in active_emps}
                    selected = st.selectbox("选择离职员工", list(options.keys()))
                    
                    if selected and st.button("办理离职"):
                        emp = options[selected]
                        for e in st.session_state.employees:
                            if e['工号'] == emp['工号']:
                                e['状态'] = '离职'
                                break
                        st.success(f"已办理 {emp['姓名']} 离职")
                        st.rerun()
                else:
                    st.info("暂无在职员工")
        
        elif operation == "办理晋升":
            if st.session_state.employees:
                active_emps = [e for e in st.session_state.employees if e.get('状态') == '在职']
                if active_emps:
                    options = {f"{e['姓名']} ({e['工号']}) - 当前: {e['职级']}": e for e in active_emps}
                    selected = st.selectbox("选择晋升员工", list(options.keys()))
                    
                    if selected:
                        emp = options[selected]
                        new_level = st.selectbox("晋升至", 
                            [l for l in st.session_state.level_standards.keys() if l != emp['职级']])
                        
                        if new_level and st.button("办理晋升"):
                            for e in st.session_state.employees:
                                if e['工号'] == emp['工号']:
                                    e['职级'] = new_level
                                    break
                            st.success(f"已办理 {emp['姓名']} 晋升至 {new_level}")
                            st.rerrun()
                else:
                    st.info("暂无在职员工")

with tab3:
    st.header("⚙️ 职级标准设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("当前职级标准")
        levels_df = pd.DataFrame([
            {'职级': level, '年度股数': shares}
            for level, shares in st.session_state.level_standards.items()
        ])
        st.dataframe(levels_df, use_container_width=True)
    
    with col2:
        st.subheader("修改职级标准")
        with st.form("level_form"):
            level = st.selectbox("选择职级", list(st.session_state.level_standards.keys()))
            shares = st.number_input("年度股数", 0, 1000000, st.session_state.level_standards[level], 1000)
            
            if st.form_submit_button("保存"):
                st.session_state.level_standards[level] = shares
                st.success(f"已更新 {level}: {shares:,} 股/年")
                st.rerun()

# 底部
st.markdown("---")
st.caption("🏢 股权激励年度股票池管理 | 简化演示版")

# 导出功能
with st.sidebar:
    st.markdown("---")
    if st.session_state.employees:
        if st.button("📥 导出员工数据"):
            df = pd.DataFrame(st.session_state.employees)
            csv = df.to_csv(index=False)
            st.download_button(
                "下载CSV",
                csv,
                "员工数据.csv",
                "text/csv"
            )
