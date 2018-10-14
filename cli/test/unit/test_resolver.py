import unittest
import sys
sys.path.append('../../')
from cruxresolver import cruxresolver


class TestCruxResolver(unittest.TestCase):

    SCHEMA_1 = """<nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
     message-id="urn:uuid:bfa51b3a-eea9-4c8c-8a8e-3b1ae416521c">
    <data
    xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">module integrationtest {
  namespace "http://brewerslabng.mellon-collie.net/yang/integrationtest";
  prefix integrationtest;

  import crux {
    prefix crux;
  }

  typedef type1 {
    type string {
      pattern "brew[a-z]*" {
        error-message
          "String must start with brew";
      }
    }
  }

  typedef type2 {
    type uint32;
  }

  typedef type3 {
    type enumeration {
      enum "A";
      enum "B";
      enum "C";
    }
  }

  typedef type4 {
    type union {
      type type3;
      type type2;
    }
  }

  leaf simpleleaf {
    type string;
  }

  container simplecontainer {
    presence "true";
  }

  list simplelist {
    key "simplekey";
    leaf simplekey {
      type string;
    }

    leaf nonleafkey {
      crux:info "A non-leaf key";
      type uint32;
      description
        "ABC";
    }
  }

  container morecomplex {
    leaf nonconfig {
      crux:info "A non-configuration node";
      type string;
      config false;
    }

    leaf leaf2 {
      crux:info "must be 1 or 0 dont sit on the fence";
      type boolean;
    }

    leaf leaf3 {
      crux:info "Should allow a string starting with brew - but no spaces";
      type type2;
    }

    leaf leaf4 {
      crux:info "Should allow A, B, C or a uint32";
      type type4;
    }

    container inner {
      presence "true";
      leaf leaf5 {
        type string;
        mandatory true;
      }

      leaf leaf6 {
        type string;
        mandatory false;
      }

      leaf leaf7 {
        type string;
        default "this-is-a-default";
      }
    }
  }
}
</data></nc:rpc-reply>"""

    def setUp(self):
        self.subject = cruxresolver()
        self.subject.register_top_tag("simpleleaf", "http://brewerslabng.mellon-collie.net/yang/integrationtest")

    # def test_basic_lookup_of_a_top_level(self):
    #    self.subject.show('')

    def test_load_simplest_ever_schema_to_memory(self):
        SCHEMA = """
        <nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
         message-id="urn:uuid:bfa51b3a-eea9-4c8c-8a8e-3b1ae416521c">
        <data
        xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
        module integrationtest {
      namespace "http://brewerslabng.mellon-collie.net/yang/integrationtest";
      prefix integrationtest;

          leaf simpleleaf {
            type string;
          }
          }
          </data></nc:rpc-reply>"""

        self.subject.load_schema_to_memory('simpleleaf', 'http://brewerslabng.mellon-collie.net/yang/integrationtest')
