import os
from dotenv import load_dotenv
from digest.config import Config
from digest.notion.rendering import NotionRenderer
from digest.notion.page_body import PageBodyBuilder
import json
load_dotenv()
cfg = Config("config.yaml").parse_config()


# print("Creating a test issue...")
# print(PageBodyBuilder.pipeline_to_mermaid(["clean HTML", "extract stories", "write to Notion"]))

# fake = {"innovation": "A new model.", "pipeline": ["a","b"], "key_points": ["x","y"]}
# body = (PageBodyBuilder()
#         .section("Summary", paragraph=fake["innovation"])
#         .mermaid_diagram("Pipeline", PageBodyBuilder.pipeline_to_mermaid(fake["pipeline"]))
#         .section("Key points", bulleted_list=fake["key_points"])
#         .build())
# import json; print(json.dumps(body, indent=2))


empty = {"innovation": "Just a summary.", "pipeline": [], "key_points": []}
body = (PageBodyBuilder()
        .section("Summary", paragraph=empty["innovation"])
        .section("Pipeline", paragraph=None, diagram_code=PageBodyBuilder.pipeline_to_mermaid(empty["pipeline"]))
        .section("Key points", paragraph=None, bulleted_list=empty["key_points"])
        .build())
print(json.dumps(body, indent=2))