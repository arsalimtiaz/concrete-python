#!/usr/bin/env python

"""
"""

from __future__ import print_function
import argparse
import logging
import os.path
import zipfile

import bottle
import humanfriendly
from thrift.protocol import TJSONProtocol
from thrift.server import TServer
from thrift.transport import TTransport

from concrete.access import FetchCommunicationService, StoreCommunicationService
from concrete.services.ttypes import ServiceInfo
from concrete.util.access import CommunicationContainerFetchHandler, RelayFetchHandler
from concrete.util.comm_container import (
    DirectoryBackedCommunicationContainer,
    MemoryBackedCommunicationContainer,
    ZipFileBackedCommunicationContainer)
from concrete.util.file_io import write_communication_to_file
from concrete.version import concrete_library_version


class AccessHTTPServer(object):
    # DANGER WILL ROBINSON!  We are using class variables
    # to store values accessed by the Bottle route functions
    # below.
    FETCH_HANDLER = None
    FETCH_TSERVER = None
    STORE_HANDLER = None
    STORE_TSERVER = None
    STATIC_PATH = None
    
    def __init__(self, host, port, static_path, fetch_handler, store_handler):
        self.host = host
        self.port = port

        AccessHTTPServer.STATIC_PATH = static_path

        AccessHTTPServer.FETCH_HANDLER = fetch_handler
        fetch_processor = FetchCommunicationService.Processor(fetch_handler)
        fetch_pfactory = TJSONProtocol.TJSONProtocolFactory()
        AccessHTTPServer.FETCH_TSERVER = TServer.TServer(
            fetch_processor, None, None, None, fetch_pfactory, fetch_pfactory)

        AccessHTTPServer.STORE_HANDLER = store_handler
        store_processor = StoreCommunicationService.Processor(store_handler)
        store_pfactory = TJSONProtocol.TJSONProtocolFactory()
        AccessHTTPServer.STORE_TSERVER = TServer.TServer(
            store_processor, None, None, None, store_pfactory, store_pfactory)
        
    def serve(self):
        bottle.run(host=self.host, port=self.port)


class DirectoryBackedStoreHandler(object):
    def __init__(self, store_path):
        self.store_path = store_path

    def about(self):
        logging.info("DirectoryBackedStoreHandler.about() called")
        service_info = ServiceInfo()
        service_info.name = 'DirectoryBackedStoreHandler'
        service_info.version = concrete_library_version()
        return service_info

    def alive(self):
        logging.info("DirectoryBackedStoreHandler.alive() called")
        return True

    def store(self, communication):
        logging.info("DirectoryBackedStoreHandler.store() called with Communication with ID '%s'" % communication.id)
        comm_filename = os.path.join(self.store_path, communication.id + '.comm')
        write_communication_to_file(communication, comm_filename)
        return


@bottle.post('/fetch_http_endpoint/')
def fetch_http_endpoint():
    return thrift_endpoint(AccessHTTPServer.FETCH_TSERVER)

@bottle.post('/store_http_endpoint/')
def store_http_endpoint():
    return thrift_endpoint(AccessHTTPServer.STORE_TSERVER)

@bottle.route('/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=AccessHTTPServer.STATIC_PATH)

def thrift_endpoint(tserver):
    """Thrift RPC endpoint for Concrete FetchCommunicationService
    """
    itrans = TTransport.TFileObjectTransport(bottle.request.body)
    itrans = TTransport.TBufferedTransport(
        itrans, int(bottle.request.headers['Content-Length']))
    otrans = TTransport.TMemoryBuffer()

    iprot = tserver.inputProtocolFactory.getProtocol(itrans)
    oprot = tserver.outputProtocolFactory.getProtocol(otrans)

    tserver.processor.process(iprot, oprot)
    bytestring = otrans.getvalue()

    headers = dict()
    headers['Content-Length'] = len(bytestring)
    headers['Content-Type'] = "application/x-thrift"
    return bottle.HTTPResponse(bytestring, **headers)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=''
    )
    parser.add_argument('fetch_source')
    parser.add_argument('--host', default='localhost',
                        help='Host interface to listen on')
    parser.add_argument('-p', '--port', type=int, default=8080)
    parser.add_argument('--static-path', default='.')
    parser.add_argument('--store-path', default='.')
    parser.add_argument('--max-file-size', type=str, default='1GiB',
                        help="Maximum size of (non-ZIP) files that can be read into memory "
                        "(e.g. '2G', '300MB')")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)7s:  %(message)s', level=logging.INFO)
    
    comm_container = {}
    if os.path.isdir(args.fetch_source):
        comm_container = DirectoryBackedCommunicationContainer(args.fetch_source)
    elif zipfile.is_zipfile(args.fetch_source):
        comm_container = ZipFileBackedCommunicationContainer(args.fetch_source)
    else:
        max_file_size = humanfriendly.parse_size(args.max_file_size, binary=True)
        comm_container = MemoryBackedCommunicationContainer(args.fetch_source,
                                                            max_file_size=max_file_size)

    fetch_handler = CommunicationContainerFetchHandler(comm_container)
    store_handler = DirectoryBackedStoreHandler(args.store_path)
    
    ahs = AccessHTTPServer(args.host, args.port, args.static_path, fetch_handler, store_handler)
    ahs.serve()

    
if __name__ == '__main__':
    main()
