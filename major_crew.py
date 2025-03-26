from crewai import Agent, Task, Crew
from crewai.project import agent, task, crew, CrewBase

@CrewBase
class Medic_Bot():
  """The Medic Bot analyzes the health report and generates comprehensive and useful insights"""

  @agent
  def report_extractor_agent(self)->Agent:
    return Agent(
    role="Extract, organize, and structure report contents into a clear and well-formatted document.",
    goal="Produce a logically structured and comprehensive report that enhances readability while preserving all information.",
    backstory="You are an expert in report structuring, ensuring that extracted content is well-organized, clearly formatted, and easy to navigate. Your role is to transform raw report data into a polished document with logical flow and coherence.",
    memory=True,
    verbose=True
    )

  @agent 
  def report_explanation_agent(self)->Agent:
    return Agent(
    role="Analyze the report received from the report_extractor_agent, evaluate all values, and determine which fall within the normal range and which deviate. ",
    goal="Generate a well-structured and comprehensive report that classifies values as normal or abnormal, explains their significance, ",
    backstory="You are an experienced pathologist specializing in interpreting blood reports with deep expertise in analyzing medical values. "
    "Your role is to evaluate, explain, and provide meaningful insights to help understand the report findings effectively.",
    memory=True,
    verbose=True
    )

  @agent
  def abnormalities_agent(self)->Agent:
    return Agent(
    role="Analyze the report received from the report_extractor, identify abnormal values, and focus on those. "
    "Provide actionable recommendations for improvement through lifestyle changes, diet, or medication where applicable. "
    "Assess the severity of abnormalities and determine if immediate medical consultation is necessary.",
    goal="Generate a structured and detailed report that highlights abnormal values, explains their significance, "
    "and provides clear, practical recommendations for improvement. Flag urgent cases for immediate medical attention.",
    backstory="You are a highly experienced medical analyst specializing in identifying health risks and providing data-driven recommendations. "
    "Your expertise lies in interpreting abnormal health metrics and offering practical guidance on managing or improving them. "
    "You ensure that users understand their health status and take appropriate action when needed.",
    memory=True,
    verbose=True
    )

  @task
  def report_extractor_task(self)->Task:
    return Task(
    description="Extract and organize the contents of the report {report} into a well-structured, coherent, and comprehensive document. "
    "Ensure logical flow, clarity, and readability by using appropriate headings, subheadings, and formatting.",
    expected_output="A complete and professionally structured report that maintains all essential information while improving organization "
    "and presentation. The final document should be clear, concise, and easy to navigate.",
    output_file="report.md",
    agent=self.report_extractor_agent()
    )

  @task
  def report_explanation_task(self)->Task:
    return Task(
      description="Analyze the structured report provided by the report_extractor_agent. "
      "Evaluate all numerical and categorical values to classify them as normal or abnormal. "
      "Assign a severity score to each abnormality and provide a detailed explanation, including potential causes, health implications, and medical recommendations. "
      "Ensure the report is structured for clarity, using headings, subheadings, and bullet points where necessary. ",
      expected_output="A well-organized, detailed medical report that: \n"
      "- Clearly classifies each value as normal or abnormal.\n"
      "- Assigns a severity score to every abnormality.\n"
      "- Provides meaningful explanations for abnormal values, including possible causes and medical implications.\n"
      "- Offers actionable recommendations where applicable.\n"
      "- Is structured with clear headings, subheadings, and bullet points for readability.\n",
      agent=self.report_explanation_agent(),
      output_file="explained_report.md"
    )

  @task
  def abnormalities_task(self)->Task:
    return Task(
     description="Analyze the report from the report_explanation_agent, focusing exclusively on abnormal values. "
     "For each abnormal metric, determine its potential health risks, explain why it is outside the normal range, "
     "and provide specific recommendations for improvement. "
     "Offer targeted advice on lifestyle changes, dietary modifications, and possible treatments. "
     "Assess the severity of each abnormality and indicate whether urgent medical consultation is required.",
     expected_output="A structured and detailed abnormalities report that:\n"
     "- Lists all abnormal values along with their medical significance.\n"
     "- Explains why these values are outside the normal range and their health implications.\n"
     "- Provides personalized recommendations, including lifestyle, dietary, and medical interventions.\n"
     "- Assigns a severity score to each abnormality (Low / Moderate / High) with justification.\n"
     "- Recommends the type of medical specialist to consult if necessary.\n"
     "- Flags severe cases that require urgent medical attention.\n"
     "- Is formatted with clear headings, subheadings, and bullet points for improved readability and usability.",
     context=[self.report_explanation_task()],
     agent=self.abnormalities_agent(),
     output_file="abnormalities.md"
    )

  @crew
  def crew(self)->Crew:
    return Crew(
      agent=[self.report_extractor_agent(),self.report_explanation_agent(), self.abnormalities_agent()],
      tasks=[self.report_extractor_task(),self.report_explanation_task(),self.abnormalities_task()]
    )
