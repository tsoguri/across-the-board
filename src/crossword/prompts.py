CLUE_GENERATION_SYSTEM_PROMPT = """
You are an expert crossword clue constructor.
Your task is to generate clues and answers based on the given information, 
excelling in creating intellectual clues that draw from a vast knowledge of 
trivia, science, history, and pop culture.

You are writing for a highly educated, intellectual audience who enjoys historical and scientific facts, 
wants to be challenged, learn new things, and remember previously known facts, references, and figures.
"""

DIFFICULTY_DESCRIPTION = {
    "Easy": "<difficulty> Easy </difficulty> \n\n Easy: Use well-known facts (e.g. historical events, people). Knowledge of a high school student. Prioritize shorter words / answers.",
    "Medium": "<difficulty> Medium </difficulty> \n\n Medium: Requires some specific historical, scientific, pop culture knowledge. Knowledge of a college graduate.",
    "Hard": "<difficulty> Hard </difficulty> \n\n Hard: Create challenging clues that may involve graduate-level historical, scientific, cultural references. Knowledge of a graduate degree.",
}

CLUE_GENERATION_PROMPT = """ 
Your task is to generate crossword clues and answers based on the following information: 

{topics}
Now, let's review the key parameters for this crossword puzzle:

{difficulty}

<num_clues>{num_clues}</num_clues>

You must generate exactly this many clues and answers.

Remember to adhere to the specified difficulty level, size constraints, and number of clues.
"""

CLUE_GENERATION_TOPIC_PROMPT = """
Here are the topics to inspire your crossword:

<topics>
{topic_str}
</topics>

Please consider these topics as you generate clues and answers. You should pull scientific, historical, cultural references from these topics as your clues.
"""


# <clue_examples>
# {clue_examples}
# </clue_examples>
