from dataclasses import dataclass, field

@dataclass
class JobOffer:
    id: str
    title: str
    company: str
    description: str
    url: str
    location: str
    source: str
    posted_date: str = ""
    raw_data: dict = field(default_factory=dict)