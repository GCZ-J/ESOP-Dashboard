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

# 简化代码，确保在Streamlit Cloud上稳定运行
def main():
    st.write("股权激励管理应用已启动！")
    st.write("这是一个演示版本，展示了股权激励预算管理的核心功能。")
    
    # 添加一些简单的演示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("股票池总额", "1,000,000 股")
    with col2:
        st.metric("已使用", "650,000 股")
    with col3:
        st.metric("剩余额度", "350,000 股")
    
    # 添加一个简单的图表
    data = pd.DataFrame({
        '部门': ['研发部', '产品部', '市场部', '销售部', '职能部'],
        '已使用股数': [200000, 150000, 120000, 100000, 80000],
        '规划需求': [250000, 180000, 150000, 120000, 100000]
    })
    
    fig = go.Figure(data=[
        go.Bar(name='已使用', x=data['部门'], y=data['已使用股数']),
        go.Bar(name='规划需求', x=data['部门'], y=data['规划需求'])
    ])
    
    fig.update_layout(
        title="各部门股权使用情况",
        barmode='group',
        xaxis_title="部门",
        yaxis_title="股数"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.info("这是一个简化版本，用于演示部署功能。完整功能包括：")
    st.markdown("""
    - 职级标准设置
    - HC规划管理
    - 员工入离职管理
    - 股权授予跟踪
    - 预算预警监控
    - 模板导入导出
    """)

if __name__ == "__main__":
    main()
