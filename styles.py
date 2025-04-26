import streamlit as st

def set_page_styling():
    """Apply general styling to the entire application"""
    # CSS is handled through custom CSS injection and config.toml
    pass

def display_custom_css():
    """Inject custom CSS for styling the application"""
    st.markdown("""
    <style>
        /* Overall styling */
        body {
            font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
            color: #333;
            background-color: #f8f9fa;
        }
        
        /* Main title styling */
        .main-title {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
        }
        
        .icon {
            margin-right: 10px;
            font-size: 1.8rem;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
        }
        
        /* Filter section */
        .filter-section {
            background-color: #fff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .filter-label {
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }
        
        /* Job card styling */
        .job-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .job-card {
            background-color: #fff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            border: 1px solid #eee;
            height: 100%;
            font-size: 0.95rem;
        }
        
        .job-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .job-card h3 {
            margin-top: 0;
            color: #333;
            font-size: 1.3rem;
        }
        
        .company {
            color: #666;
            margin-bottom: 15px;
        }
        
        .job-tag {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 15px;
            font-size: 0.8rem;
            margin-right: 8px;
            margin-bottom: 10px;
        }
        
        .location {
            background-color: #e8f4f8;
            color: #0077b6;
        }
        
        .experience {
            background-color: #f0f8ea;
            color: #5a9216;
        }
        
        .salary {
            font-weight: bold;
            color: #e86a33;
            margin-bottom: 10px;
        }
        
        .skills {
            color: #666;
            margin-bottom: 15px;
            font-size: 0.9rem;
        }
        
        .view-btn, .apply-btn {
            display: inline-block;
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9rem;
            margin-right: 10px;
            margin-top: 10px;
        }
        
        .view-btn {
            background-color: #4dabf7;
            color: white;
            width: 100%;
            text-align: center;
        }
        
        .back-btn {
            display: inline-block;
            margin-bottom: 20px;
            padding: 8px 16px;
            background-color: #f1f3f5;
            color: #495057;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background-color 0.2s;
        }
        
        .back-btn:hover {
            background-color: #e9ecef;
        }
        
        /* Job detail styling */
        .job-detail {
            background-color: #fff;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .job-detail h2 {
            margin-top: 0;
            color: #333;
            font-size: 1.6rem;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        
        .detail-section {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .detail-item {
            background-color: #f8f9fa;
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        
        .info-label {
            font-weight: bold;
            color: #0066CC;
            min-width: 50px;
            display: inline-block;
        }
        
        .description {
            white-space: pre-line;
            line-height: 1.6;
            margin-bottom: 20px;
            color: #495057;
            font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
            font-size: 1rem;
        }
        
        .task-item {
            padding: 5px 0 5px 20px;
            position: relative;
            color: #495057;
            font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
        }
        
        .task-item:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #0066CC;
            font-weight: bold;
        }
        
        .benefits-section {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 5px solid #28a745;
        }
        
        .benefit-item {
            margin-bottom: 8px;
            line-height: 1.5;
            color: #495057;
            padding: 5px 0;
            font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
            font-size: 1rem;
        }
        
        /* Resume section */
        .resume-section {
            background-color: #fff;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        /* Analysis results */
        .analysis-results {
            background-color: #fff;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        
        .success-rate {
            font-size: 1.2rem;
            margin-bottom: 20px;
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            display: inline-block;
        }
        
        .rate-value {
            font-weight: bold;
            color: #4dabf7;
        }
        
        .analysis-section {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            height: 100%;
        }
        
        .strengths {
            border-left: 4px solid #5cb85c;
        }
        
        .improvements {
            border-left: 4px solid #f0ad4e;
        }
        
        .analysis-item {
            margin-bottom: 10px;
            padding: 5px 0;
        }
        
        .recommendations {
            margin-top: 20px;
        }
        
        .recommendation-item {
            background-color: #f1f8e9;
            padding: 12px 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 4px solid #8bc34a;
        }
        
        .download-btn {
            display: inline-block;
            padding: 8px 15px;
            background-color: #4dabf7;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 15px;
        }
        
        /* 자격 요건 스타일 */
        .qualification-section {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .qualification-item {
            margin-bottom: 15px;
            padding: 12px;
            background-color: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .qualification-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .qualification-name {
            font-weight: bold;
            font-size: 1.05rem;
        }
        
        .qualification-status {
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .qualification-bar-container {
            width: 100%;
            height: 25px;
            background-color: #e9ecef;
            border-radius: 5px;
            margin: 5px 0;
            position: relative;
        }
        
        .qualification-bar {
            height: 100%;
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            transition: width 0.5s ease;
        }
        
        .qualification-score {
            color: white;
            font-weight: bold;
            font-size: 0.8rem;
        }
        
        .qualification-desc {
            margin-top: 8px;
            font-size: 0.9rem;
            color: #495057;
            line-height: 1.4;
        }
        
        /* 자격 요건 스타일 */
        .requirement-section {
            margin: 30px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
            border-left: 5px solid #0066CC;
        }
        
        .qualification-item {
            padding: 12px 0;
            border-bottom: 1px dashed #e0e0e0;
            line-height: 1.5;
        }
        
        .qualification-item:last-child {
            border-bottom: none;
        }
        
        .qualification-label {
            font-weight: bold;
            color: #0066CC;
            min-width: 90px;
            display: inline-block;
        }
        
        /* 역량 지표 스타일 */
        .competency-section {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .competency-item {
            margin-bottom: 15px;
            padding: 10px;
            background-color: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .competency-name {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 1rem;
        }
        
        .competency-bar-container {
            width: 100%;
            height: 25px;
            background-color: #e9ecef;
            border-radius: 5px;
            margin: 5px 0;
            position: relative;
        }
        
        .competency-bar {
            height: 100%;
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            transition: width 0.5s ease;
        }
        
        .competency-score {
            color: white;
            font-weight: bold;
            font-size: 0.8rem;
        }
        
        .competency-desc {
            margin-top: 8px;
            font-size: 0.9rem;
            color: #495057;
            line-height: 1.4;
        }
        
        /* Footer */
        footer {
            text-align: center;
            color: #6c757d;
            padding: 20px 0;
            font-size: 0.9rem;
            border-top: 1px solid #eee;
            margin-top: 40px;
        }
    </style>
    """, unsafe_allow_html=True)

def create_progress_bar(percentage, color="#0066CC"):
    """
    Create a colored progress bar with the given percentage
    
    Args:
        percentage (float): Value between 0 and 100
        color (str): Hex color code for the progress bar
    """
    # Normalize percentage
    normalized = max(0, min(100, percentage)) / 100
    
    # Using Streamlit's progress bar
    st.progress(normalized)
