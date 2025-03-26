from crewai import Agent, Task, Crew
from crewai.project import agent, task, crew, CrewBase
from crewai_tools import SerperDevTool
import os

from google.colab import userdata
SERP_API_KEY=userdata.get('SERP_API_KEY')
os.environ['SERP_API_KEY']=SERP_API_KEY

@CrewBase
class Doctor_Bot():
  """This bot will find the best doctors for the user"""

  @agent
  def doctor_finder_agent(self)->Agent:
    return Agent(
        role="Doctor Finder Agent",
        goal="Find the best doctors specializing in the detected abnormalities and provide their contact details.",
        backstory="You are an AI-powered healthcare assistant with access to live search tools. "
        "Based on the patient's abnormal blood report parameters, you search for specialists (hematologists, endocrinologists, cardiologists, etc.) "
        "and recommend the most relevant doctors in the patient's location.",
        tools=[SerperDevTool()], 
        verbose=True,
        memory=True
    )

  @task
  def doctor_finder_task(self)->Task:
    return Task(
        description="Search for top-rated doctors specializing in the following abnormalities: {abnormalities}. \n"
        "Ensure the recommended doctors are located in or near {user_city}. \n"
        "For each specialist, provide:\n"
        "1️⃣ Doctor's Name\n"
        "2️⃣ Specialization (e.g., Endocrinologist, Hematologist, Cardiologist)\n"
        "3️⃣ Clinic/Hospital Name\n"
        "4️⃣ Contact Information (Phone/Email)\n"
        "5️⃣ Consultation Options (In-person or Online)\n"
        "6️⃣ Any relevant patient reviews or ratings (if available).",
        expected_output=
        "A list of specialists, including their names, specialization, clinic details, "
        "contact information, and consultation options, stored in `doctors.md`.",
        agent=self.doctor_finder_agent(),
        output_file="doctors.md"
    )

  @crew
  def crew(self)->Crew:
    return Crew(
      agents=[self.doctor_finder_agent()],
      tasks=[self.doctor_finder_task()]
    )
  
