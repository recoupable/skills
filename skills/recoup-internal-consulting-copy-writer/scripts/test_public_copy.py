import tempfile
import unittest
from pathlib import Path
from check_public_copy import check, public_text, DEFAULT_TERMS

class PublicCopyTests(unittest.TestCase):
    def test_private_frontmatter_is_not_exported(self):
        text='---\nsource: signals/music-moneyball.md\nstatus: draft\n---\nA clear original explanation.'
        self.assertNotIn('signals/', public_text(text,'.md'))
    def test_public_title_is_checked(self):
        self.assertIn('Music Fastball',public_text('---\ntitle: Music Fastball\n---\nBody','.md'))
    def test_html_skips_code_but_checks_alt(self):
        text='<style>.music-moneyball{}</style><img alt="Music Fastball"><h1>Readable title</h1>'
        self.assertEqual(public_text(text,'.html'),'Music Fastball Readable title')
    def test_excluded_reference_and_private_footer_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'article.md';p.write_text('Music Moneyball says...\nSource: clients/example/notes.md')
            self.assertEqual(len(check(p,DEFAULT_TERMS)['blocking_flags']),2)
    def test_supplier_not_presumed_competitor(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'article.md';p.write_text('Check the output from your Claude workflow.')
            result=check(p,DEFAULT_TERMS)
            self.assertEqual(result['blocking_flags'],[])
            self.assertIn('plain-language',result['manual_review_required'])
    def test_configured_name_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'article.md';p.write_text('A quote from EXAMPLE RIVAL.')
            self.assertEqual(check(p,['Example Rival'])['blocking_flags'],['excluded-reference: Example Rival'])
if __name__=='__main__': unittest.main()
