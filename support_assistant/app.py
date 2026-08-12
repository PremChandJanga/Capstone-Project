from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from graph import support_graph
from schemas import SupportResponse


app = FastAPI(
    title="Zepto Support Assistant",
    description="RAG-based Zepto customer support assistant",
    version="1.0.0"
)


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Customer support question"
    )


@app.get("/")
def root():
    return {
        "message": "Zepto Support Assistant API is running"
    }


@app.post("/ask", response_model=SupportResponse)
def ask(request: AskRequest):

    try:
        result = support_graph.invoke(
            {
                "question": request.question
            }
        )

        return SupportResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            confidence=1.0
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process the question: {exc}"
        )