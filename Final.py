import csv
from datetime import datetime
from collections import defaultdict
import sys
import os 

# ======================================================================
# 1. Configuration and Hardcoded Data (The "Document Data" to be analyzed)
#    配置与硬编码数据 (待分析的“文档数据”)
# ======================================================================

# Keywords indicating negative sentiment for risk analysis
# 用于风险分析的负面情绪关键词
NEGATIVE_WORDS = ["bug", "delay", "risk", "difficulty", "blocker", "error", 
                  "failure", "challenge", "problem", "poor", "crash", "tricky"]

# CSV File Name (assuming it's in the same directory)
# CSV 文件名（假设与脚本在同一目录下）
CSV_FILE_NAME = "project_data.csv"

# ======================================================================
# 2. Data Model (ProjectRecord Class) - 修复 from_row
#    数据模型 (ProjectRecord 类) - Fixed from_row
# ======================================================================

class ProjectRecord:
    """
    Represents a single record from the project work log.
    Data Fields: [Date], [Module], [Duration(hours)], [Status/Sentiment], [Summary]
    代表项目工作日志中的一条记录。
    """
    def __init__(self, date_str, module, duration, status, summary):
        self.date_str = date_str
        self.module = module.strip()
        
        try:
            # Attempt to convert the date string to a datetime object
            # 尝试将日期字符串转换为 datetime 对象
            self.date = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except ValueError:
            # Mark the date as invalid upon parsing error
            # 标记日期无效，如果解析出错
            self.date = None 

        try:
            # Attempt to convert the duration to a float
            # 尝试将持续时间转换为浮点数
            self.duration = float(duration)
        except ValueError:
            # Mark the duration as 0.0 upon parsing error
            # 如果解析出错，标记持续时间为 0.0
            self.duration = 0.0

        self.status = status.strip()
        # Convert summary to lowercase for case-insensitive sentiment analysis
        # 将摘要转换为小写，以便进行不区分大小写的情感分析
        self.summary = summary.strip().lower()

    @classmethod
    def from_row(cls, row):
        """Creates a ProjectRecord instance from a CSV row (list)"""
        # 从 CSV 行（列表）创建 ProjectRecord 实例
        
        # 修复逻辑: 确保行至少有 5 个字段，并只使用前 5 个字段，忽略任何多余的尾随字段。
        # Fix Logic: Ensure the row has at least 5 fields, and only use the first 5, ignoring any extra trailing fields.
        if len(row) < 5:
            return None
            
        # 明确地将 row 列表截断为前 5 个元素，以匹配 __init__ 所需的 5 个参数。
        # Explicitly slice the row to the first 5 elements to match the 5 arguments needed by __init__.
        return cls(*row[:5]) # <--- 关键修复 (The critical fix)

    def is_valid(self):
        """Checks if the record is valid (valid date and positive duration)"""
        # 检查记录是否有效（有效日期和正持续时间）
        return self.date is not None and self.duration > 0

    def has_negative_sentiment(self):
        """Checks if the summary contains any negative keywords"""
        # 检查摘要是否包含任何负面关键词
        for word in NEGATIVE_WORDS:
            if word in self.summary:
                return True
        return False
    
    def __repr__(self):
        """String representation for easy debugging"""
        # 便于调试的字符串表示
        return f"Record(Date={self.date_str}, Mod={self.module}, Dur={self.duration}h)"

# ======================================================================
# 3. Data Parser - 文件读取逻辑 (File Reading Logic)
# ======================================================================

class DataParser:
    """Responsible for parsing data from a physical CSV file."""
    # 负责从物理 CSV 文件解析数据。
    def __init__(self, file_path):
        # file_path is the path to the CSV file
        # file_path 是 CSV 文件的路径
        self.file_path = file_path
        self.records = []
        self.error_count = 0

    def load_data(self):
        """Loads all records from the CSV file."""
        # 从 CSV 文件加载所有记录。
        
        # Check if the file exists
        # 检查文件是否存在
        if not os.path.exists(self.file_path):
            print(f"Fatal Error: CSV file not found at '{self.file_path}'", file=sys.stderr)
            return False
        
        # Use with open() to safely open and read the file
        # 使用 with open() 安全地打开和读取文件
        try:
            # newline='' is recommended for CSV reading to prevent blank rows on different OS
            # newline='' 建议用于 CSV 读取，以防止在不同操作系统上出现空行问题
            with open(self.file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                # Skip the header row
                # 跳过标题行
                next(reader, None) 
                
                for i, row in enumerate(reader, start=2):
                    # Skip empty lines
                    # 跳过空行
                    if not any(row): continue 
                    
                    record = ProjectRecord.from_row(row)
                    if record and record.is_valid():
                        self.records.append(record)
                    else:
                        self.error_count += 1
            
            print(f"Data parsing complete. Loaded {len(self.records)} valid records from '{self.file_path}', skipped {self.error_count} error records.")
            return True
            
        except Exception as e:
            print(f"Fatal error during data parsing: {e}", file=sys.stderr)
            return False

# ======================================================================
# 4. Analyzer (Business Logic) - 保持不变 (No Change)
#    分析器 (业务逻辑)
# ======================================================================

class ProjectAnalyzer:
    """Responsible for multi-dimensional analysis of the records"""
    # 负责对记录进行多维分析
    def __init__(self, records):
        self.records = records
        self.analysis_results = {}

    def analyze_time_efficiency(self):
        """Analyzes total work duration and time span"""
        # 分析总工时和时间跨度
        if not self.records:
            self.analysis_results['time'] = {"total_duration": 0.0, "avg_daily": 0.0}
            return

        total_duration = sum(r.duration for r in self.records)
        
        # Calculate work days (count of unique dates)
        # 计算工作日（唯一日期的数量）
        dates = [r.date for r in self.records]
        start_date = min(dates)
        end_date = max(dates)
        work_days = len(set(dates))
        
        avg_daily = total_duration / work_days if work_days > 0 else 0.0
        
        self.analysis_results['time'] = {
            "total_duration": total_duration,
            "work_days": work_days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "avg_daily": avg_daily
        }

    def analyze_module_load(self):
        """Analyzes the percentage of time spent on each module"""
        # 分析每个模块花费的时间百分比
        module_duration = defaultdict(float)
        
        for r in self.records:
            module_duration[r.module] += r.duration
            
        total_duration = sum(module_duration.values())
        
        # Calculate percentages and store results
        # 计算百分比并存储结果
        module_load = {}
        for module, duration in module_duration.items():
            percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
            module_load[module] = {"duration": duration, "percentage": percentage}

        # Sort by duration in descending order for report clarity
        # 按持续时间降序排序，使报告更清晰
        sorted_modules = sorted(module_load.items(), key=lambda item: item[1]['duration'], reverse=True)
        
        self.analysis_results['modules'] = sorted_modules
        self.analysis_results['total_duration'] = total_duration 

    def analyze_risk(self):
        """Analyzes potential risk index (negative sentiment ratio)"""
        # 分析潜在风险指数（负面情绪比率）
        if not self.records:
            self.analysis_results['risk'] = {"negative_count": 0, "total_count": 0, "top_words": []}
            return

        negative_records = [r for r in self.records if r.has_negative_sentiment()]
        negative_count = len(negative_records)
        total_count = len(self.records)

        # Count the frequency of negative keywords
        # 统计负面关键词的频率
        word_counts = defaultdict(int)
        for r in negative_records:
            for word in NEGATIVE_WORDS:
                if word in r.summary:
                    word_counts[word] += 1
        
        # Get the top three most frequent negative words
        # 获取出现频率最高的前三个负面关键词
        top_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)[:3]
        
        self.analysis_results['risk'] = {
            "negative_count": negative_count,
            "total_count": total_count,
            "top_words": top_words
        }

    def run_all_analysis(self):
        """Executes all analysis components"""
        # 执行所有分析组件
        self.analyze_time_efficiency()
        self.analyze_module_load()
        self.analyze_risk()
        return self.analysis_results

# ======================================================================
# 5. Report Generator - 保持不变 (No Change)
#    报告生成器
# ======================================================================

class ReportGenerator:
    """Responsible for formatting and printing the analysis results to the terminal"""
    # 负责格式化并将分析结果打印到终端
    def __init__(self, analysis_results):
        self.results = analysis_results
        self.line_width = 70 # Standard width for terminal output / 终端输出的标准宽度

    def print_separator(self, char='='):
        """Prints a horizontal separator line"""
        # 打印水平分隔线
        print(char * self.line_width)

    def generate_time_report(self):
        """Generates the time efficiency report"""
        # 生成时间效率报告
        time_data = self.results.get('time', {})
        self.print_separator('-')
        print(f"[1] Time Efficiency Analysis / 时间效率分析")
        self.print_separator('-')
        
        if time_data.get("total_duration", 0) == 0:
            print("  No valid work duration data. / 无有效工时数据。")
            return
            
        print(f"  Project Span:     {time_data['start_date']} to {time_data['end_date']}")
        print(f"  Total Duration:   {time_data['total_duration']:.1f} hours / 总工时")
        print(f"  Total Work Days:  {time_data['work_days']} days / 总工作日")
        print(f"  Avg Daily Work:   {time_data['avg_daily']:.2f} hours / 日均工时")

    def generate_module_report(self):
        """Generates the module workload report with ASCII bar chart"""
        # 生成带 ASCII 条形图的模块工作量报告
        module_data = self.results.get('modules', [])
        total_duration = self.results.get('total_duration', 1)
        
        self.print_separator('-')
        print(f"[2] Module Workload Breakdown (Total {total_duration:.1f} hours) / 模块工作量细分")
        self.print_separator('-')
        
        if not module_data:
            print("  No module workload data. / 无模块工作量数据。")
            return
            
        max_bar_width = 30 # Max width for the ASCII chart / ASCII 图的最大宽度
        
        for module, data in module_data:
            duration = data['duration']
            percentage = data['percentage']
            
            # Calculate the length of the ASCII bar
            # 计算 ASCII 条的长度
            bar_length = int(percentage / 100 * max_bar_width)
            bar = '#' * bar_length
            
            # Format output, using alignment to keep the chart starting point clean
            # 格式化输出，使用对齐保持图表起点的整洁
            info_str = f"{module}: {duration:.1f}h ({percentage:.1f}%)"
            print(f"{info_str:<{self.line_width - max_bar_width - 3}} | {bar}")

    def generate_risk_report(self):
        """Generates the potential risk analysis report"""
        # 生成潜在风险分析报告
        risk_data = self.results.get('risk', {})
        self.print_separator('-')
        print(f"[3] Potential Risk Analysis (Based on Negative Keywords) / 潜在风险分析")
        self.print_separator('-')
        
        total = risk_data.get("total_count", 0)
        negative = risk_data.get("negative_count", 0)
        
        if total == 0:
            print("  No records available for risk analysis. / 无可用记录进行风险分析。")
            return

        negative_percent = (negative / total) * 100
        print(f"  Total Records:           {total} entries / 总记录数")
        print(f"  Records with Risk Words: {negative} entries ({negative_percent:.1f}%) / 含风险词记录数")
        
        # AI Risk Assessment Logic
        # AI 风险评估逻辑
        if negative_percent >= 30:
            assessment = "HIGH RISK / 高风险"
        elif negative_percent >= 15: 
            assessment = "MEDIUM RISK / 中等风险"
        else:
            assessment = "LOW RISK / 低风险"
            
        print(f"  AI Risk Assessment:      **{assessment}** / AI 风险评估")
        
        top_words = risk_data.get('top_words', [])
        if top_words:
            print("\n  Most Frequent Negative Keywords: / 最常出现的负面关键词:")
            for word, count in top_words:
                print(f"  - '{word.capitalize()}' occurred {count} times / 出现次数")

    def generate_full_report(self, title="Project Health Analysis Report / 项目健康分析报告"):
        """Generates the complete, cohesive report"""
        # 生成完整、一致的报告
        self.print_separator('=')
        print(f"{title:^{self.line_width}}")
        self.print_separator('=')
        
        self.generate_time_report()
        self.generate_module_report()
        self.generate_risk_report()
        
        self.print_separator('=')
        print(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_separator('=')

# ======================================================================
# 6. Main Execution Logic / 主执行逻辑
# ======================================================================

def run_analysis():
    """Main function to run the system analysis"""
    # 运行系统分析的主函数
    print("\n--- Welcome to the File-Based Project Report Analyzer / 欢迎使用文件式项目报告分析器 ---\n")
    
    # 1. Data Parsing (uses the CSV_FILE_NAME constant)
    # 1. 数据解析 (使用 CSV_FILE_NAME 常量)
    parser = DataParser(CSV_FILE_NAME)
    if not parser.load_data():
        print("\nSystem terminated due to data parsing failure. / 系统因数据解析失败而终止。")
        return

    if not parser.records:
        print("\nNo valid records were loaded, analysis cannot proceed. / 未加载有效记录，分析无法进行。")
        return

    # 2. Data Analysis
    # 2. 数据分析
    analyzer = ProjectAnalyzer(parser.records)
    analysis_results = analyzer.run_all_analysis()

    # 3. Report Generation
    # 3. 报告生成
    reporter = ReportGenerator(analysis_results)
    reporter.generate_full_report()

if __name__ == "__main__":
    run_analysis()
