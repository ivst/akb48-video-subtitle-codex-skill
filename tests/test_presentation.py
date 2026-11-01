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
from check_presentation import check_coverage


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
        ass,tracks,warnings=render(self.data,self.episode)
        self.assertTrue(warnings)
        # An unestablished voice is published without any label or placeholder.
        self.assertNotIn('Голос ?',ass)
        self.assertNotIn('Voice ?',ass)
        self.assertIn(r'\pos(960,',ass)
        self.assertIn('\nТы уже выбрала ответ?\n', tracks['dialogue'])
        self.assertNotIn('Участница А: Ты уже выбрала ответ?', tracks['dialogue'])

    def test_placeholder_labels_are_rejected(self):
        for label in ('Голос ?', 'Голос 1', 'Голос №2', 'Voice ?1', 'Voice 2',
                      'Unknown 3', '未知聲音 1', '未知声音 2'):
            with self.subTest(label=label):
                self.data['speakers']['a']['label'] = label
                self.assertTrue(any('placeholder label' in e for e in validate(self.data,self.episode)[0]))

    def test_source_coverage_rejects_dropped_turns_and_allows_explicit_splits(self):
        source = [{'id': key, 'text': 'source'} for key in self.data['turns']]
        self.assertEqual(check_coverage(self.data, source), [])
        # Keeping the turn in notes must not hide its absence in display events.
        self.data['events'] = [e for e in self.data['events'] if e['id'] != 'd2']
        self.assertTrue(any('t2' in e for e in check_coverage(self.data, source)))
        source = [{'id': '001', 'text': 'one original caption'}]
        for turn in self.data['turns'].values():
            turn['source_ids'] = ['001']
        self.assertEqual(check_coverage(self.data, source), [])
        self.data['turns']['t1']['source_ids'] = ['invented']
        self.assertTrue(any('not in scoped source' in e for e in check_coverage(self.data, source)))
        self.data['turns']['t1']['source_ids'] = '001'
        self.assertTrue(any('array' in e for e in check_coverage(self.data, source)))

    def test_sign_source_coverage_and_generated_output_are_checked_together(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = [{'id': key, 'text': 'source'} for key in self.data['turns']]
            source.append({'id': 'sign-original', 'text': 'sign', 'kind': 'inscription'})
            sign = next(e for e in self.data['events'] if e['kind'] == 'inscription')
            sign['source_ids'] = ['sign-original']
            self.assertEqual(check_coverage(self.data, source), [])
            for name, data in [('presentation.json', self.data), ('episode.json', self.episode),
                               ('source.json', {'cues': source})]:
                (root / name).write_text(json.dumps(data), encoding='utf-8')
            flags = ['--input', str(root/'presentation.json'), '--episode', str(root/'episode.json')]
            result = subprocess.run([sys.executable, str(SKILL/'scripts/build_presentation.py'),
                                     *flags, '--output-dir', str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            command = [sys.executable, str(SKILL/'scripts/check_presentation.py'), *flags,
                       '--source', str(root/'source.json'), '--ass', str(root/'subtitles.ru.ass'), '--json']
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            source.append({'id': 'lost', 'text': 'missing dialogue'})
            (root/'source.json').write_text(json.dumps({'cues':source}), encoding='utf-8')
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('missing from presentation: lost', result.stdout)

    def test_paired_exchange_cannot_hide_an_unnamed_voice(self):
        event = next(e for e in self.data['events'] if len(e.get('rows', [])) == 2)
        row = event['rows'][0]
        row['speaker_id'] = None
        for key in row['source_ids']:
            self.data['turns'][key]['speaker_id'] = None
        errors, _ = validate(self.data, self.episode)
        self.assertTrue(any('two established voices' in e for e in errors))

    def test_style_overrides_keep_dialogue_and_speaker_mapping(self):
        _, original_tracks, _ = render(self.data, self.episode)
        self.data['style'] = {
            'panel_x': 80, 'panel_width': 1760, 'panel_fill': '#EAF4FC',
            'panel_border': '#38B5D5', 'panel_opacity': 1,
            'dialogue_color': '#112233', 'sign_fill': '#235E78',
            'sign_border': '#F4D24A', 'sign_color': '#FFFFDD',
        }
        ass, tracks, _ = render(self.data, self.episode)
        self.assertEqual(original_tracks, tracks)
        self.assertIn(r'\pos(80,968)', ass)
        self.assertIn(r'\pos(1055,', ass)
        self.assertIn(r'\1c&HFCF4EA&\1a&H00&', ass)
        self.assertIn(r'\3c&HD5B538&', ass)
        self.assertIn('Style: Speech,Segoe UI Semibold,40,&H00332211', ass)
        self.assertIn(',Speech,a,', ass)
        self.assertIn(',Speech,b,', ass)

    def test_invalid_style_settings_fail_instead_of_silent_fallback(self):
        for style in [None, {'panel_x': -1}, {'panel_width': 1920},
                      {'panel_width': 1199}, {'panel_opacity': float('nan')},
                      {'panel_opacity': True}, {'panel_opacity': 0.2},
                      {'dialogue_color': 'red'}, {'sign_font_size': 99},
                      {'unrecognized_color': '#FFFFFF'}]:
            with self.subTest(style=style):
                self.data['style'] = style
                self.assertTrue(validate(self.data, self.episode)[0])
                with self.assertRaises(ValueError):
                    render(self.data, self.episode)

    def test_sign_override_and_font_size_affect_fit_checks(self):
        sign = next(e for e in self.data['events'] if e['kind'] == 'inscription')
        sign['style'] = {'sign_fill': '#112233', 'sign_color': '#223344', 'sign_font_size': 30}
        sign['box'] = [100, 200, 1500, 180]
        ass, _, _ = render(self.data, self.episode)
        self.assertIn(r'\1c&H332211&', ass)
        self.assertIn(r'\fs30\1c&H443322&', ass)
        sign['box'] = [100, 200, 1500, 43]
        with self.assertRaisesRegex(ValueError, 'box too small'):
            render(self.data, self.episode)
        sign['style'] = {'panel_width': 1500}
        self.assertTrue(validate(self.data, self.episode)[0])
        self.data['events'][0]['style'] = {'sign_color': '#223344'}
        self.assertTrue(any('only supported for signs' in e for e in validate(self.data, self.episode)[0]))

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
        self.data['style'] = {'panel_border': '#38B5D5', 'sign_fill': '#235E78'}
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
