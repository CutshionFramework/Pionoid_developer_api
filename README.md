## Open ai voice control requirement
choco install ffmpeg -y

## Robot Instances Management

### why Redis

- **High Performance**: Redis is an in-memory data store, providing extremely fast read and write operations.
- **Efficient Caching**: Ideal for caching robot instances, reducing initialization overhead.
- **Session Management**: Perfect for managing session tokens and related data with low latency.

### Installing Redis on Windows
```sh
wsl --install
sudo apt update
sudo apt install redis-server
sudo service redis-server start
wsl --list --verbose            
redis-cli ping
sudo systemctl enable redis-server #run redis on start

sudo nano /etc/redis/redis.conf    #open config standard dir
bind 0.0.0.0                       #change bind to accept any IP
sudo service redis-server restart  #restart


wsl -d Ubuntu  # when opening a new cmd in Windows to initiate Linux CLI
redis-cli -h 127.0.0.1 -p 6379
KEYS * # to check all keys


## License 
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.