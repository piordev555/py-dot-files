#! /usr/bin/env python3

from __future__ import division, print_function, unicode_literals

import asyncio
import re
import subprocess as sb
import sys

WAIT_TIME = 1.75


class BluetoothctlProtocol(asyncio.SubprocessProtocol):
    def __init__(self, exit_future, echo=True):
        self.exit_future = exit_future
        self.transport = None
        self.output = None
        self.echo = echo

    def pipe_data_received(self, fd, raw):
        d = raw.decode()
        if self.echo:
            print(d, end='')

        if self.output is not None:
            self.output += d

    def listen_output(self):
        self.output = ''

    def not_listen_output(self):
        self.output = None

    def connection_made(self, transport):
        self.transport = transport
        print('Connection MADE')

    async def send_command(self, c):
        stdin_transport = self.transport.get_pipe_transport(0)
        stdin_transport._pipe.write(('%s\n' % c).encode())

    async def send_and_wait(self, cmd, wait_expression, fail_expression='fail'):
        try:
            self.listen_output()
            await self.send_command(cmd)
            while not await self.search_in_output(wait_expression.lower(), fail_expression=fail_expression):
                await wait()
        finally:
            self.not_listen_output()

    async def search_in_output(self, expression, fail_expression=None):
        if self.output is None:
            return None

        for l in self.output.splitlines():
            if fail_expression and re.search(fail_expression, l, re.IGNORECASE):
                raise Exception('Expression "%s" failed with fail pattern: "%s"' % (l, fail_expression))

            if re.search(expression, l, re.IGNORECASE):
                return True

    async def disconnect(self, mac):
        await self.send_and_wait('disconnect %s' % (mac), 'Successful disconnected', fail_expression='Failed')

    async def connect(self, mac):
        await self.send_and_wait('connect %s' % (mac), 'Connection successful')

    def process_exited(self):
        self.exit_future.set_result(True)

    async def scan(self, mode):
        await self.send_command('scan %s' % mode)

    async def power(self, mode):
        await self.send_command('power %s' % mode)

    async def quit(self):
        await self.send_command('quit')


async def wait():
    return await asyncio.sleep(WAIT_TIME)


async def execute_command(cmd):
    p = await asyncio.create_subprocess_shell(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
    stdout, stderr = await p.communicate()
    stdout, stderr = \
        stdout.decode() if stdout is not None else '', \
        stderr.decode() if stderr is not None else ''
    if p.returncode != 0 or stderr.strip() != '':
        print('Command: %s failed with status: %s\nstderr: %s' % (cmd, p.returncode, stderr))
    return stdout


async def set_profile(device_id, profile='a2dp_sink'):
    cmd = 'pactl set-card-profile %s %s' % (device_id, profile)
    print(cmd)
    return await execute_command(cmd)


async def main():

    # My own JBL
    mac = 'FC:A8:9A:B9:45:14'
    device_id = 'bluez_card.FC_A8_9A_B9_45_14'

    # # Mani's Sony SRS-X3
    # mac = '0C:A6:94:7C:E4:40'
    # device_id = 'bluez_card.0C_A6_94_7C_E4_40'

    # # Jesica's
    # mac = '40:EF:4C:68:57:58'
    # device_id = 'bluez_card.40_EF_4C_68_57_58'

    exit_future = asyncio.Future()
    transport, protocol = await asyncio.get_event_loop().subprocess_exec(
        lambda: BluetoothctlProtocol(exit_future, echo=True), 'bluetoothctl')

    await set_profile(device_id, profile='off')
    await protocol.power('on')
    await protocol.scan('on')
    await protocol.disconnect(mac)
    await protocol.connect(mac)
    await protocol.quit()
    transport.close()

    # try multiple times to set the proper profile
    await wait()
    await set_profile(device_id, profile='a2dp_sink')
    await wait()
    await set_profile(device_id, profile='a2dp_sink')

    await exit_future
    print('Exit')


if __name__ == '__main__':
    sys.exit(asyncio.get_event_loop().run_until_complete(main()))
