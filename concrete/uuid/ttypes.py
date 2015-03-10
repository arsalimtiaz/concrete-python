#
# Autogenerated by Thrift Compiler (0.9.1)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:new_style,utf8strings
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class UUID(object):
  """
  Attributes:
   - uuidString: A string representation of a UUID, in the format of:
  <pre>
  550e8400-e29b-41d4-a716-446655440000
  </pre>
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'uuidString', None, None, ), # 1
  )

  def __init__(self, uuidString=None,):
    self.uuidString = uuidString

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.uuidString = iprot.readString().decode('utf-8')
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('UUID')
    if self.uuidString is not None:
      oprot.writeFieldBegin('uuidString', TType.STRING, 1)
      oprot.writeString(self.uuidString.encode('utf-8'))
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.uuidString is None:
      raise TProtocol.TProtocolException(message='Required field uuidString is unset!')
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.uuidString)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
