from crewai.flow import Flow, start, listen, and_, or_, router
from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel
from major_crew import Medic_Bot
from doctor_crew import Doctor_Bot
import nest_asyncio
nest_asyncio.apply()

class State(BaseModel):
  abnormalities:str=" "
  decision:str=" "
  report:str=" "


class MediTrustAI(Flow[State]):

  @start()
  def medic_bot(self):
    report=PyPDFLoader("/content/WM17S.pdf")
    report=report.load()
    report= "\n\n".join([doc.page_content for doc in report])
    self.state.report=report
    result=(
        Medic_Bot().crew().kickoff({"report":self.state.report})
    )
    self.state.abnormalities=result.raw

  @listen(medic_bot)
  def ask(self):
    decision=input("Would you like to have a list of recommended doctors")
    self.state.decision=decision

  @router(ask)
  def route(self):
    x=self.state.decision
    if(x=="yes"):
      return "Proceed"
    else:
      return "Dont Proceed"

  @listen("Proceed")
  def doctor_bot(self):
    user_city=input("Enter your city")
    result=(
        Doctor_Bot().crew().kickoff({"user_city":user_city,"abnormalities":self.state.abnormalities})
    )
