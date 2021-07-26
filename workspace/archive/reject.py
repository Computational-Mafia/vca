    # they need to have 'vote' or 'veot' early in their string
    #early_enough = []
    #for i in range(len(boldtags)):
    #    first_three_words = ' '.join(boldtags[i].split(' ')[:3]).lower()
    #    if (first_three_words.count('vote') or 
    #        first_three_words.count('veot') > 0 or 
    #        first_three_words.count('vtoe') > 0 or 
    #        first_three_words.count('ovte') > 0):
    #        early_enough.append(True)
    #    else:
    #        early_enough.append(False)

    #boldtags = [boldtags[i] for i in range(len(boldtags)) if early_enough]

# %%
# length = 10
# n_item = int(df['position'].max())
# n_list = int(df['wagon'].max())
# list_lim = (0, n_list + 1)
# item_lim = (0, n_item + 1)
# x_var, y_var = 'wagon', 'position'
# x_lim, y_lim = list_lim, item_lim
# x_label, y_label = 'Wagon', 'Vote Position'
# def_aspect = n_list / n_item
# height = length / def_aspect

# g = sns.FacetGrid(
#         data=df, dropna=False, height=8, col='voted_faction')
# g.map_dataframe(
#         sns.scatterplot,
#         x=y_var,
#         y=x_var,
#         marker='s',
#         hue='voter_faction',
#         legend='auto',
#     )

# #g.set_xlabels(x_label)
# #g.set_ylabels(y_label)
# #g.set(xlim=x_lim, ylim=y_lim)

# %% [markdown]
# # Wagon Raster Plotting
# Here we want to demo a potential way to streamline visualization of many game wagons: a raster plot of a subset of wagons hued based on the faction of the person making the vote. With that foundation we might be set up to work on more complex visualizations (e.g. tracking changes in wagon sizes across a phase) or to perform contrastive statistical tests.

# %% [markdown]
# ## Setup
# For each D1 the votecounter successfully predicts w/o help (and a lynch has happened), simulate votecounter until a hammer is detected. match each vote to a faction. The sequence is what we want in our DF. The raster plot is effectively a scatter plot tracking 3 variables. I need in my df for each vote a wagon index, a position on wagon, and a faction. Since the number of votes required to achieve a lynch can vary, I may be interested in aligning position indices such that hammer votes all have the same x-position rather than such that initial votes all have the same x-position.