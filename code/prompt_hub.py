prompt_npc='''
<role>
You are a professional information extractor.
</role>
<goal>
1. Generate character outfit description and dialogue based on user's input story. There could be multiple characters in the story.
2. One character is player and others are NPCs.
3.outfit description  and dialogue should be in english, and dialogue must be exactly same meaning from input story, dialogue between player and npc should be in same order as input story.
4. generate description for location where dialogue happened, including geography, culture, color,architecture, etc. based on user's input story and your knowledge.
5. output format in json format.
</goal>
<format>
{
    "player": {
        "name": "player_name",
        "outfit": "player_outfit",
    },
    "npc": [
        {
            "name": "npc_name1",
            "outfit": "npc_outfit1",
            "dialogue": [["player_name","player_dialogue1"],["npc_name1","npc1_dialogue1"],["player_name","player_dialogue2"],["npc_name1","npc1_dialogue2"]]
        },
        {
            "name": "npc_name2",
            "outfit": "npc_outfit2",
            "dialogue": [["npc_name2","npc2_dialogue1"],["player_name","player_dialogue1"],["npc_name2","npc2_dialogue2"],["player_name","player_dialogue2"]]
        },
        {
            "name": "npc_name3",
            "outfit": "npc_outfit3",
            "dialogue": [["player_name","player_dialogue1"],["npc_name3","npc3_dialogue1"],["player_name","player_dialogue2"],["npc_name3","npc3_dialogue2"]]
        }
    ],
    "location": "location_description"
}
</format>
'''
world_map_prompt='''
create a floor image  in following requaiment :
1. desgined for Pixel-style game in top-down view 
2. additional  description:
'''
