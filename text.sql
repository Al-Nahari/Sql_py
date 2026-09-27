-- SQLite
-- this is inner
select * from students where student_id = (select student_id from assessments where score >= 90);

select * from emp , dept 
where emp.dept_id = dept.id and dept_name = "sales"

select s.student_id , s.full_name, AVG(a.scor) as average_scor
from students s
join assessments a on s.student_id = a.student_id
group by s.student_id,s.full_name 
having AVG(a.score) > (select AVG(score) from assessments)

select s.student_id , s.full_name
from students s
where exists (select 1 from assessments a where a.student_id = s.student_id and a.score > 90)

select s.student_id, s.full_name
from students s
where exists (
  select 1 from assessments a
  where a.student_id = s.student_id and a.score > 90
);

select s.student_id, s.full_name, AVG(a.score) as average_score
from students s
join assessments a on s.student_id = a.student_id
group by s.student_id, s.full_name
having AVG(a.score) > (select AVG(score) from assessments);

select * 
from (select s.student_id, AVG(a.score) as average_score from students s,assessments a group by s.student_id) as student_avg where average_score >= 80;


with student_averges as (select student_id,AVG(a.score) as average_score from assessments group by s.student_id)


select *
from students s
where exists (
  select 1 from assessments a
  where a.student_id = s.student_id and a.score > 90
); 

with student_averages as (
  select student_id, AVG(score) as average_score
from assessments
  group by student_id
)
select * from student_averages;



select count(*) as total_students,
sum(case when score >= 90 then 1 else 0 end) as excellent_count,
sum(case when score >= 80 and score < 90 then 1 else 0 end) as very_good_count,
sum(case when score >= 70 and score < 80 then 1 else 0 end) as good_count,
sum(case when score < 60 then 1 else 0 end) as poor_count
from assessments;

select student_id, score, AVG(score) over (partition by student_id) as student_average from assessments;


with student_averages as (
  select student_id, AVG(score) as average_score
from assessments
  group by student_id
)
select student_id,average_score,dense_rank() over(order by average_score desc )as student_rank from student_averages;


select student_id, score, lead(score) over (partition by student_id order by assessment_id) as previous_score from assessments;
select student_id, score,
       lag(score) over (partition by student_id order by assessment_id) as previous_score
from assessments;

with student_averages as (
  select student_id, AVG(score) as average_score
from assessments
  group by student_id
)
select student_id,average_score,rank() over(order by student_id desc )as student_rank from student_averages;

