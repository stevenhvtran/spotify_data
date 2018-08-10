import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import rcParams

# Display options for plots and tables
rcParams.update({'figure.autolayout': True})
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)

# Load in my Spotify data
df = pd.read_csv('data.csv', index_col=0)

# Add extra column for track duration in seconds
df['duration_sec'] = df['duration_ms']/1000

# Converted added_at to Datetime object
df['added_at'] = pd.to_datetime(df['added_at'],
                                format='%Y-%m-%dT%H:%M:%SZ',
                                utc=True)

grouped_df = df.groupby(['playlist_name', 'playlist_id', 'track_name',
                         'track_id', 'artist_name', 'artist_id'])

# Data frame of unique tracks in every playlist
playlist_tracks = df.groupby(['playlist_name'])['track_name'].unique()

# Data frame of each artists songs in a playlist
artist_tracks_playlist = df.groupby(['artist_name', 'playlist_name'])
artist_tracks_playlist = artist_tracks_playlist.agg(lambda x: x.tolist())
# Count of number of tracks a playlist per artist
num_artists_tracks_playlist = artist_tracks_playlist['track_name'].str.len()
num_artists_tracks_playlist.sort_values(ascending=False, inplace=True)
top_artists_playlist = num_artists_tracks_playlist.head(15)
# Plot for num times artist appears in a playlist
"""
plot_title = 'Number of times an artist appeared in a playlist'
top_artists_playlist.plot('barh', title=plot_title)
plt.savefig('./Plots/artists_tracks_num_playlists')
"""

# Data frame of each artists songs
artist_tracks = df.groupby(['artist_name']).agg(lambda x: x.tolist())
# Count of number of tracks of an artist I have
num_artists_tracks = artist_tracks['track_name'].str.len()
num_artists_tracks = num_artists_tracks.sort_values(ascending=False)
top_artists = num_artists_tracks.head(15)
# Plot for num times artist appears in my playlists
"""
plot_title = 'Number of times an artist appears in my playlists'
top_artists.plot('barh', title=plot_title)
plt.savefig('./Plots/artists_tracks_num')
"""

# Cleaned up data frame with artists grouped into lists
df2 = df.groupby(
    [
        'track_name', 'playlist_name', 'album_name', 'added_at', 'duration_ms',
        'duration_sec', 'explicit', 'popularity', 'track_id', 'playlist_id',
        'album_id'
    ]).agg(lambda x: x.tolist()).reset_index()

# Average explicitness of every playlist
explicit_playlists = df2.groupby(['playlist_name'])['explicit'].mean()
explicit_playlists = explicit_playlists.sort_values()
# Plot of explicitness of playlists
"""
explicit_playlists.plot('barh', title='Explicitness of playlists')
plt.savefig('./Plots/explicitness_playlists')
"""
