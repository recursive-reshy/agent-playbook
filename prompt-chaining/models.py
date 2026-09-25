from pydantic import BaseModel, Field

class OutlineSection( BaseModel ):
    heading: str = Field( description = "Section heading" )
    key_points: list[ str ] = Field( description = "2-4 points this section should cover" )

class Outline( BaseModel ):
    title: str = Field( description = "Blog post title" )
    sections: list[ OutlineSection ]

class BlogPost( BaseModel ):
    topic: str
    outline: Outline
    draft: str
    final: str