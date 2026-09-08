#!/bin/bash

cp config.toml ~/.config/feeds-to-instapaper/config.toml
sudo cp *.service /etc/systemd/system/
sudo cp *.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable feeds-to-instapaper.timer
sudo systemctl start feeds-to-instapaper.timer
sudo systemctl enable feed-fulltext-scraper.timer
sudo systemctl start feed-fulltext-scraper.timer

