"""Prevent the real-trial failures: mixed voices, unsolicited lyrics and raised panels."""
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL=Path(__file__).resolve().parents[1]/'.agents/skills/akb48-video-subtitles'
sys.path.insert(0,str(SKILL/'scripts'))
from presentation import render,validate


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((SKILL/'assets/presentation.example.json').read_text(encoding='utf-8'))
        self.episode=json.loads((SKILL/'assets/presentation.settings.json').read_text(encoding='utf-8'))

    def test_visible_labels_lower_baseline_and_separate_tracks(self):
        ass,tracks,_=render(self.data,self.episode)
        self.assertIn(',Speech,a,',ass)
        self.assertIn(',Speech,b,',ass)
        self.assertIn('Участница А:',tracks['dialogue'])
        self.assertIn('Участница Б:',tracks['dialogue'])
        self.assertNotIn('Викторина',tracks['dialogue'])
        self.assertIn('Викторина',tracks['inscriptions'])
        self.assertEqual(tracks['lyrics'],'')
        self.assertIn(r'\pos(110,968)',ass) # 82px panel, bottom=1050 => 30px margin.

    def test_published_ass_is_generated_from_the_installed_example(self):
        expected, _, _ = render(self.data, self.episode)
        published = SKILL.parents[2] / 'examples' / 'compact.ass'
        self.assertEqual(published.read_text(encoding='utf-8-sig'), expected)

    def test_unknown_preset_cannot_silently_change_style(self):
        self.data['style_preset'] = 'plain-text-boxes'
        with self.assertRaisesRegex(ValueError, 'unsupported style_preset'):
            render(self.data, self.episode)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg unavailable')
    def test_real_previews_keep_lower_baseline_and_expand_upwards(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([
                sys.executable, str(SKILL/'scripts/render_style_previews.py'),
                '--output-dir', folder, '--font', 'Arial'
            ], capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            def pixel(name, x, y):
                result = subprocess.run([
                    'ffmpeg', '-nostdin', '-v', 'error', '-i', str(Path(folder)/name),
                    '-vf', f'format=rgb24,crop=1:1:{x}:{y}', '-frames:v', '1',
                    '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'
                ], capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(result.stdout), 3)
                return min(result.stdout)
            for name in ('compact-single-preview.jpg', 'compact-preview.jpg',
                         'compact-long-preview.jpg'):
                self.assertGreater(pixel(name, 90, 680), 230) # Light panel.
                self.assertLess(pixel(name, 90, 710), 160) # Lower margin stays clear.
            self.assertLess(pixel('compact-single-preview.jpg', 90, 610), 160)
            self.assertGreater(pixel('compact-preview.jpg', 90, 610), 230)
            self.assertGreater(pixel('compact-long-preview.jpg', 90, 630), 230)

    def test_mixed_known_speakers_cannot_be_merged(self):
        self.data['events'][0]['rows'][0]['source_ids']=['t1','t2']
        errors,_=validate(self.data,self.episode)
        self.assertTrue(any('different speaker' in e for e in errors))

    def test_unknown_does_not_mean_same_speaker(self):
        self.data['turns']['u1']={'speaker_id':None}
        self.data['turns']['u2']={'speaker_id':None}
        row=self.data['events'][0]['rows'][0]
        row.update(speaker_id=None,source_ids=['u1','u2'])
        self.assertTrue(any('unknown speakers' in e for e in validate(self.data,self.episode)[0]))
        row['source_ids']=['u1']
        ass,_,warnings=render(self.data,self.episode)
        self.assertTrue(warnings)
        self.assertIn('Голос ?',ass)

    def test_dash_or_slash_dialogue_must_be_reviewed(self):
        for text in ('— Я знаю. — А я нет.','Да! / Нет!'):
            self.data['events'][0]['rows'][0]['text']=text
            self.assertTrue(any('mixed voices' in e for e in validate(self.data,self.episode)[0]))

    def test_lyrics_require_explicit_request_and_background_kind_is_rejected(self):
        self.data['events'].append({'id':'l1','start_ms':0,'end_ms':1000,'kind':'lyrics','text':'Synthetic lyric'})
        self.assertTrue(any('not explicitly requested' in e for e in validate(self.data,self.episode)[0]))
        self.episode['lyrics_policy']='requested'
        self.assertTrue(any('lyrics_request' in e for e in validate(self.data,self.episode)[0]))
        self.episode['lyrics_request']='User explicitly requested a lyric translation for the demo.'
        _,tracks,_=render(self.data,self.episode)
        self.assertIn('Synthetic lyric',tracks['lyrics'])
        self.data['events'][-1]['kind']='background_music'
        self.assertTrue(validate(self.data,self.episode)[0])

    def test_raised_dialogue_requires_reason_and_long_text_is_not_shrunk(self):
        self.data['bottom_margin']=144 # The trial used 96px at 720p.
        with self.assertRaisesRegex(ValueError,'placement reason'):render(self.data,self.episode)
        self.data['bottom_margin']=30
        self.data['events'][0]['rows'][0]['text']='Long dialogue ' * 100
        with self.assertRaisesRegex(ValueError,'split long dialogue'):render(self.data,self.episode)

    def test_output_drift_and_stale_lyrics_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            data=root/'presentation.json';data.write_text(json.dumps(self.data),encoding='utf-8')
            episode=root/'episode.json';episode.write_text(json.dumps(self.episode),encoding='utf-8')
            args=['--input',str(data),'--episode',str(episode)]
            built=subprocess.run([sys.executable,str(SKILL/'scripts/build_presentation.py'),*args,
                                  '--output-dir',str(root)],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            flags=[*args,'--ass',str(root/'subtitles.ru.ass'),'--srt',str(root/'dialogue.ru.srt'),'--json']
            def check():
                return subprocess.run([sys.executable,str(SKILL/'scripts/check_presentation.py'),*flags],
                                      capture_output=True,text=True)
            self.assertEqual(check().returncode,0)
            ass=root/'subtitles.ru.ass';original=ass.read_text(encoding='utf-8-sig')
            ass.write_text(original.replace('Участница А','Hidden'),encoding='utf-8')
            self.assertEqual(check().returncode,1)
            ass.write_text(original,encoding='utf-8')
            sign=root/'inscriptions.ru.srt';correct_sign=sign.read_text(encoding='utf-8-sig')
            sign.write_text('Outdated sign translation',encoding='utf-8')
            self.assertEqual(check().returncode,1)
            sign.write_text(correct_sign,encoding='utf-8')
            (root/'lyrics.ru.srt').write_text('Stale song fragment',encoding='utf-8')
            self.assertEqual(check().returncode,1)

    def test_legacy_trial_without_speaker_contract_fails(self):
        errors,_=validate({'dialogue':[{'text':'— Hi. — Hello.'}],'lyrics':[]},self.episode)
        self.assertTrue(errors)

    def test_translation_chunks_do_not_request_lyrics_implicitly(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            src=root/'source.json';out=root/'translated.json';ep=root/'episode.json'
            src.write_text(json.dumps({'cues':[{'id':'l1','kind':'lyrics','text':'Test lyric'}]}),encoding='utf-8')
            out.write_text(json.dumps({'cues':[{'id':'l1','text':'Example translation'}]}),encoding='utf-8')
            flags=[sys.executable,str(SKILL/'scripts/check_translation.py'),'--input',str(src),
                   '--translated',str(out),'--episode',str(ep),'--json']
            ep.write_text(json.dumps({'lyrics_policy':'omit'}),encoding='utf-8')
            result=subprocess.run(flags,capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('excluded by default',result.stdout)
            ep.write_text(json.dumps({'lyrics_policy':'requested','lyrics_request':'Please translate these performance lyrics.'}),encoding='utf-8')
            self.assertEqual(subprocess.run(flags,capture_output=True,text=True).returncode,0)


if __name__=='__main__':unittest.main()
