SYSTEM_INSTRUCTION = """You are an expert in academic writing and citation formatting. 
                    Your task is to:
                    1. Insert **inline citations** where appropriate based on the provided sources. 
                    2. **Enclose** any directly lifted statements in quotation marks.
                    3. Generate a **properly formatted Bibliography ** in {format} style using the given sources.

                    Ensure that:
                    - Citations follow {format} formatting guidelines.
                    - The response is structured in **valid JSON format** with clear fields for the formatted text and Bibliography.
                    """
USER_INSTRUCTION =  """
   **Sources:**
   {sources}

   using {format} style , provide inline citations and generate a bibliography for the texts below.
   {text}
- ONLY use quotation marks for directly lifted statements and append the citation to the end of the sentence.
- Only cite texts that have a semantic match to a source.
- If no semantic match exists leave the text as it is.  
- Ensure every intext citation corresponds to a reference and are accurately mapped.
   
Return the response in JSON format with  the fields listed below and no accompanying text:
   - `"formatted_text"`: The text with inline citations.
   - `"references"`: List of references used  for the inline citations in {format} format. 
                     "formatted reference in {format} format",
                     "formatted reference in {format} format",
                     ...
                     ]
   - `"validation_notes"`: Optional. A list of notes explaining the citation decisions.
Note: If no intext citation, return an empty list for the references.

- REFERENCE DEDUPLICATION:
                        - Compare reference details of the article name and author if the same, keep the most complete reference.
                        - When duplicates are found, merge them into a single reference entry,remove the duplicate and update the intext citation accordingly.
                    
                    """
MERGE_CITATION_INSTRUCTION = """
                  I have multiple JSON-formatted citation responses that contain different parts of an article. 
                  Each response includes a formatted_text field with the article's content and a references field listing sources.

                  Task:
                  Merge the formatted_text fields into a single coherent article.
                  Text:
                  {text}

                  sample response:
                  {{
                    "formatted_text": string,  # The merged article.
                    "references": [            # list of unrepeated references formatted in {format} style.
                        string,
                        ...
                    ]

                    validate your response by adhering to the following rules:
                    - The merged text is coherent and complete.
                    - The merged text has all references and they are correctly formatted.
                    - When references are adjusted, ensure the intext citation mapped to it is adjusted accordingly.
                    -If no intext citation, return an empty list for the references and leave text unchanged.
                    
                    - REFERENCE DEDUPLICATION:
                        - Compare reference details of the article name and author if the same, keep the most complete reference.
                        - When duplicates are found, merge them into a single reference entry,remove the duplicate and update the intext citation accordingly.
                    
                  }}
"""