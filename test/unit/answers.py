class answers:

    SCHEMA_CRUX_WHEN_LEAFREF = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <default cruxpath="/default" cruxtype="leaf" cruxleaftype="string" cruxdefault="stausquo"/>
    <whencontainer cruxpath="/whencontainer" cruxtype="container" cruxcondition="../default=\\'statusquo\\'">
      <then cruxpath="/whencontainer/then" cruxtype="leaf" cruxleaftype="string" cruxdefault="thendefault"/>
    </whencontainer>
    <thing-that-is-lit-up-for-C cruxpath="/thing-that-is-lit-up-for-C" cruxtype="leaf" cruxleaftype="string" cruxcondition="../thing-that-is-used-for-when=\\'C\\'"/>
    <thing-to-leafref-against cruxpath="/thing-to-leafref-against" cruxtype="leaf" cruxleaftype="string"/>
    <thing-that-is-leafref cruxpath="/thing-that-is-leafref" cruxtype="leaf" cruxleaftype="leafref" cruxleafref="../thing-to-leafref-against"/>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/default</path>
    <path>/whencontainer</path>
    <path>/whencontainer/then</path>
    <path>/thing-that-is-lit-up-for-C</path>
    <path>/thing-to-leafref-against</path>
    <path>/thing-that-is-leafref</path>
  </crux-paths>
</crux-schema>
"""
    SCHEMA_CRUX_EXPECTED = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <crux-cli cruxpath="/crux-cli" cruxtype="container">
      <modules cruxpath="/crux-cli/modules" cruxtype="list" cruxkey="module">
        <module cruxpath="/crux-cli/modules/module" cruxtype="leaf" cruxleaftype="string"/>
        <namespace cruxpath="/crux-cli/modules/namespace" cruxtype="leaf" cruxleaftype="string" cruxmandatory="yes"/>
        <revision cruxpath="/crux-cli/modules/revision" cruxtype="leaf" cruxleaftype="string"/>
        <top-level-tags cruxpath="/crux-cli/modules/top-level-tags" cruxtype="list" cruxkey="tag">
          <tag cruxpath="/crux-cli/modules/top-level-tags/tag" cruxtype="leaf" cruxleaftype="string"/>
        </top-level-tags>
      </modules>
    </crux-cli>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/crux-cli</path>
    <path>/crux-cli/modules</path>
    <path>/crux-cli/modules/module</path>
    <path>/crux-cli/modules/namespace</path>
    <path>/crux-cli/modules/revision</path>
    <path>/crux-cli/modules/top-level-tags</path>
    <path>/crux-cli/modules/top-level-tags/tag</path>
  </crux-paths>
</crux-schema>
"""

    SCHEMA_TYPES_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <simpleleaf cruxpath="/simpleleaf" cruxtype="leaf" cruxleaftype="string"/>
    <simplecontainer cruxpath="/simplecontainer" cruxtype="presence-container"/>
    <morecomplex cruxpath="/morecomplex" cruxtype="container">
      <nonconfig cruxpath="/morecomplex/nonconfig" cruxtype="leaf" cruxleaftype="string" cruxconfig="no"/>
      <leaf2 cruxpath="/morecomplex/leaf2" cruxtype="leaf" cruxleaftype="boolean"/>
      <inner cruxpath="/morecomplex/inner" cruxtype="presence-container">
        <leaf5 cruxpath="/morecomplex/inner/leaf5" cruxtype="leaf" cruxleaftype="string" cruxmandatory="yes"/>
        <leaf6 cruxpath="/morecomplex/inner/leaf6" cruxtype="leaf" cruxleaftype="enumeration" cruxenum0="A" cruxenum1="B" cruxenum2="C" cruxenum="3"/>
        <leaf7 cruxpath="/morecomplex/inner/leaf7" cruxtype="leaf" cruxleaftype="string" cruxdefault="this-is-a-default"/>
      </inner>
    </morecomplex>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/simpleleaf</path>
    <path>/simplecontainer</path>
    <path>/morecomplex</path>
    <path>/morecomplex/nonconfig</path>
    <path>/morecomplex/leaf2</path>
    <path>/morecomplex/inner</path>
    <path>/morecomplex/inner/leaf5</path>
    <path>/morecomplex/inner/leaf6</path>
    <path>/morecomplex/inner/leaf7</path>
  </crux-paths>
</crux-schema>
"""

    SCHEMA_GROUPING_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <resolver cruxpath="/resolver" cruxtype="container">
      <a cruxtype="leaf" cruxleaftype="string"/>
    </resolver>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/resolver</path>
  </crux-paths>
</crux-schema>
"""

    SCHEMA_UNION_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <type2 cruxpath="/type2" TODO should this go???? its a typedef >
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
    <uuuuuuuu cruxpath="/uuuuuuuu" cruxtype="leaf" cruxleaftype="union"/>
      <yin-schema>
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

    SCHEMA_CHOICE_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <FIRSTOPTION cruxpath="/FIRSTOPTION" cruxtype="leaf" cruxleaftype="string"/>
    <SECONDOPTION cruxpath="/SECONDOPTION" cruxtype="leaf" cruxleaftype="string"/>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/FIRSTOPTION</path>
    <path>/SECONDOPTION</path>
  </crux-paths>
</crux-schema>
"""
