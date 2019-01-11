class answers:

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
