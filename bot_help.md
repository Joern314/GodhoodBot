## GodhoodWB- Wiki - Bot

The Bot is run by the GM at some times of the day / whenever needed.

It downloads all the reddit comments and the wiki, and searches for new / changed wiki entries.

A wiki entry has the format 

```
    ##### <Name> [<Category>]
    
    Info: /u/<creator> [Turn X](<link to comment>)
    
    <Description Text>
```

The "Info Line" is allowed to be absent. If the entry is from a comment,
then the bot will try to insert it using the name of the author, and link of the comment.

The Description Text can go over several lines and be arbitrarily formatted. It must not contain headlines (`##`) 
or horizontal separators (`---`). 

You can end the description text with a headline or separator.

The Category is the name of any headline found in the wiki (e.g. `Regions` or `Mortal Races`). 
If there already is a wiki entry before the current one, with a higher level headline (less `#`), then you can leave out the 
category, it will then be sorted as a child entry of the previous one.

Editing the wiki or comments works just fine, the bot will detect the change.

Here is an example for a valid comment with wiki entries.

```
    ## Chapter One

    In the beginning the god of fire made his own lands:

    ### Continent of Dööm [Regions]
    Lots of volcanoes here.
    
    * Mount Doom
    * Eternal Lava Sea
    
    #### Eternal Lava Sea
    **Info:** /u/joern314 [Turn 2](...)
    
    **Description:** A big sea of lava, duh!

    **Origin**: Made by the god of lava
    ---

    Then he gave the mortals a spell:
    
    #### Blessed Earth Spell [Magic]
    Bless the earth!

    ---

    And it was very good!
```