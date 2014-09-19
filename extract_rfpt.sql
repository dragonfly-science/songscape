DROP table if exists rftp_scores;
CREATE temporary table rftp_scores AS 
select
    s.id, 
    a.analysis_id,
    selection_method, 
    date_part('year', r.datetime) as year, 
    date_part('month', r.datetime) as month, 
    date_part('day', r.datetime) as day, 
    site.code as site, 
    recorder.code as recorder, 
    slow.score as low,
    speak.score as peak,
    shigh.score as high,
    skiwi.score as kiwi,
    a.male_kiwi,
    a.female_kiwi,
    a.uncertain
from 
    recordings_snippet s
left join
    (select
        an.id as analysis_id,
        snippet_id,
        selection_method,
        coalesce(male_kiwi, 0) as male_kiwi,
        coalesce(female_kiwi, 0) as female_kiwi,
        coalesce(uncertain, 0) as uncertain
    from
        recordings_analysisset an
    left join
        (select 
            analysisset_id,
            sum((tag_id=1)::INTEGER) as male_kiwi,
            sum((tag_id=2)::INTEGER) as female_kiwi,
            sum((tag_id=3)::INTEGER) as uncertain
        from 
            recordings_calllabel c
        group by 
            analysisset_id 
        )  as calls
    on calls.analysisset_id = an.id
        and an.analysis_id = 1
    ) as a
    on s.id = a.snippet_id
left join
    recordings_recording r
    on s.recording_id = r.id
left join 
    recordings_deployment d
    on r.deployment_id = d.id
left join 
    recordings_site site
    on d.site_id = site.id
left join 
    recordings_recorder recorder
    on d.recorder_id = recorder.id
left join recordings_score skiwi
    on  skiwi.snippet_id = s.id
        and skiwi.detector_id = 4
left join recordings_score slow
    on  slow.snippet_id = s.id
        and slow.detector_id = 5
left join recordings_score shigh
    on  shigh.snippet_id = s.id
        and slow.detector_id = 6
left join recordings_score speak
    on  speak.snippet_id = s.id
        and speak.detector_id = 7
where
    d.owner_id = 1
    --and selection_method is not null
;

\copy rftp_scores to 'rftp_scores.csv' with csv header
