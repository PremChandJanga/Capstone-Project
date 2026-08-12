from pydantic import BaseModel, Field


class SupportResponse(BaseModel):
    answer: str = Field(
        description="Answer to the user's support question"
    )

    sources: list[str] = Field(
        default_factory=list,
        description="Source documents used to answer the question"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )


def create_support_response(
    answer: str,
    sources: list[str],
    confidence: float
) -> SupportResponse:

    return SupportResponse(
        answer=answer,
        sources=sources,
        confidence=confidence
    )


if __name__ == "__main__":

    response = create_support_response(
        answer="Zepto delivery typically takes 10 to 30 minutes.",
        sources=["doc_01.txt"],
        confidence=0.95
    )

    print("\n" + "=" * 60)
    print("TASK 4 — STRUCTURED OUTPUT TEST")
    print("=" * 60)

    print("\nPydantic Object:")
    print(response)

    print("\nJSON:")
    print(response.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("STRUCTURED OUTPUT TEST PASSED")
    print("=" * 60)