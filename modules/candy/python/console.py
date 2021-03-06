import os
import struct
import base64
import random
from d3des import deskey
from server import get_server, get_arg, response, append, space, path

# Generate key
def generate_key(password):
  c_password = (password + '\x00' * 8)[:8]
  encrypted = deskey(c_password, False)
  encrypted_bytes = struct.pack('i' * 32, *encrypted)
  encrypted_string = base64.b64encode(encrypted_bytes)
  key = (encrypted_string)
  return key

# Base directory
base = os.path.dirname(os.path.realpath(__file__))

serve = get_server()

if not serve:
  response(False)

address = get_arg('ip[ip]')

try:
  machine = serve.get_vm_by_name(address)
except:
  response(False)
  
# Server address
server_address = get_arg('server[ip]')
  
# VMware port
first = random.randint(9000, 9999)

# Port and Password
port = get_arg('port')
password = get_arg('password')

# Generate key
key = generate_key(password)

# VMware version
version = get_arg('server[virtualization]')

settings = {
  'RemoteDisplay.vnc.enabled': 'TRUE',
  'RemoteDisplay.vnc.password': password
}

if '5.x' in version or '6.0' in version:
  settings.update({'remotedisplay.vnc.port': str(first)})
  
  try:
    machine.set_extra_config(settings)
  except:
    response(False)
  
else:
  settings.update({'RemoteDisplay.vnc.port': str(first), 'RemoteDisplay.vnc.key': key})

  try:
    online = machine.is_powered_on()
  except:
    response(False)
    
  if online:
    try:
      machine.power_off()
    except:
      response(False)
      
  try:
    machine.set_extra_config(settings)
  except:
    response(False)
    
  try:
    machine.power_on()
  except:
    response(False)

# VNC address
vnc_address = append(server_address, ':', first)

try:
  os.system(space('bash', path(base, '..', '..', '..', 'web/console/utils/launch.sh'), '--vnc', vnc_address, '--listen', port, '> /dev/null 2>&1 &'))
except:
  response(False)
  
response(True)