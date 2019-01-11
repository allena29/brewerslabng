class answers:

    SCHEMA_UNION_EXPECTED1 = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <typedef name="type2">
    </typedef>
  <typedef name="type3">
    </typedef>
  <leaf name="uuuuuuuu">
    <type name="union">
      <type name="string"/>
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  <type name="uint32"/>
  </type>
  </leaf>
</module>
"""

    SCHEMA_UNION_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <type2>
      <yin-schema path="/type2">
        <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type2">
    </typedef>
      </yin-schema>
    </type2>
    <type3>
      <yin-schema path="/type3">
        <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type3">
    </typedef>
      </yin-schema>
    </type3>
    <uuuuuuuu>
      <yin-schema path="/uuuuuuuu">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="uuuuuuuu">
    <type name="union">
      <type name="string"/>
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  <type name="uint32"/>
  </type>
  </leaf>
      </yin-schema>
    </uuuuuuuu>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/type2</path>
    <path>/type3</path>
    <path>/uuuuuuuu</path>
  </crux-paths>
</crux-schema>
"""

    SCHEMA_CHOICE_EXPECTED1 = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
<namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
<prefix value="integrationtest"/>
  <choice name="MAKEYOURMINDUP">
    <case name="OPTION1">
      <leaf name="FIRSTOPTION">
        <crux:info>
          <crux:text>choice</crux:text>
        </crux:info>
        <type name="string"/>
      </leaf>
    </case>
    <case name="OPTION2">
      <leaf name="SECONDOPTION">
        <type name="string"/>
      </leaf>
    </case>
  </choice>
</module>
"""

    SCHEMA_CHOICE_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <FIRSTOPTION>
      <yin-schema path="/FIRSTOPTION">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="FIRSTOPTION">
        <crux:info>
          <crux:text>choice</crux:text>
        </crux:info>
        <type name="string"/>
      </leaf>
      </yin-schema>
    </FIRSTOPTION>
    <SECONDOPTION>
      <yin-schema path="/SECONDOPTION">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="SECONDOPTION">
        <type name="string"/>
      </leaf>
      </yin-schema>
    </SECONDOPTION>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/FIRSTOPTION</path>
    <path>/SECONDOPTION</path>
  </crux-paths>
</crux-schema>
"""
