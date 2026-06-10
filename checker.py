name: Auto IPTV Link Checker

on:
  schedule:
    - cron: '0 */6 * * *' # প্রতি ৬ ঘণ্টা পর পর অটোমেটিক রান হবে
  workflow_dispatch: # ম্যানুয়ালি রান করার অপশন

jobs:
  check-links:
    runs-on: ubuntu-latest
    permissions:
      contents: write # কোডের ভেতর থেকেও আমরা পারমিশন নিশ্চিত করে দিলাম
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4 # ভার্সন আপডেট করা হয়েছে (Node 24 এর জন্য)

    - name: Set up Python
      uses: actions/setup-python@v5 # ভার্সন আপডেট করা হয়েছে
      with:
        python-version: '3.10' # এখানে আগের ভুলটি ঠিক করা হয়েছে

    - name: Install Dependencies
      run: pip install requests

    - name: Run Link Checker Script
      run: python checker.py

    - name: Commit and Push Active Playlist
      run: |
        git config --global user.name "SCNBD Bot"
        git config --global user.email "bot@scnbd.tv"
        git add active_channels.m3u
        git commit -m "Auto Update: Active Channels Playlist" || exit 0
        git push
