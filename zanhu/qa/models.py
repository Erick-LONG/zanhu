from __future__ import unicode_literals
import uuid
from collections import Counter
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation

from django.db import models
from slugify import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from taggit.managers import TaggableManager


@python_2_unicode_compatible
class Vote(models.Model):
    '''使用Django中的contentType，同时关联用户对问题和回答的投票'''
    uuid_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='qa_vote',on_delete=models.CASCADE,verbose_name='用户')
    value = models.BooleanField(default=True,verbose_name='赞成or反对') #true赞同

    #genericForeignKey设置
    content_type = models.ForeignKey(ContentType,related_name='votes_on',on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255) #其他模型类的主键ID
    vote = GenericForeignKey('content_type','object_id')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name='投票'
        verbose_name_plural = verbose_name
        unique_together = ('user','content_type','object_id')#联合唯一键 某用户只能对某条数据赞或踩只能操作一次
        #SQL优化
        index_together = ('content_type','object_id') #联合唯一索引


@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):
    '''自定义queryset,提高模型类的可用性'''
    def get_answered(self):
        '''已有答案的问题'''
        return self.filter(has_answer=True)

    def get_unanswered(self):
        '''未被回答的问题'''
        return self.filter(has_answer=False)

    def get_counted_tags(self):
        '''统计所有问题标签的数量- 大于0'''
        tag_dict = {}
        query = self.all().annotate(tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


@python_2_unicode_compatible
class Question(models.Model):
    STATUS = (
        ('O','Open'),
        ('C','Close'),
        ('D','Draft'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,on_delete=models.CASCADE,
                             related_name='qauthor',verbose_name='提问者')
    title = models.CharField(max_length=255,unique=True,verbose_name='标题')
    slug = models.SlugField(max_length=255, verbose_name='URL别名')
    status = models.CharField(max_length=1, choices=STATUS, default='O', verbose_name='问题状态')
    content = MarkdownxField(verbose_name='内容')
    tags = TaggableManager(help_text='多个标签使用英文逗号隔开', verbose_name='标签')
    has_answer = models.BooleanField(default=False,verbose_name='接受回答')#是否有接受的回答
    votes = GenericRelation(Vote,verbose_name='投票情况')#不是实际的字段

    created_at = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    objects = QuestionQuerySet.as_manager()



    class Meta:
        verbose_name = '问题'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def save(self, *args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question,self).save(*args,**kwargs)

    def __str__(self):
        return self.title

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        '''得票数'''
        dic = Counter(self.votes.values_list('value',flat=True)) #赞同数多少，反对数多少
        return dic[True] - dic[False]

    def get_answers(self):
        return Answer.objects.filter(question=self)

    def count_answers(self):
        return self.get_answers.count()

    def get_upvoters(self):
        '''赞同的用户'''
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        '''反对的用户'''
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_accecpted_answer(self):
        return Answer.objects.get(question=self,is_answer = True)


@python_2_unicode_compatible
class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='a_author',on_delete=models.CASCADE,verbose_name='回答者')
    question = models.ForeignKey(Question,on_delete=models.CASCADE,verbose_name='问题')
    content = MarkdownxField(verbose_name='内容')
    is_answer = models.BooleanField(default=False,verbose_name='回答是否被接受')
    votes = GenericRelation(Vote, verbose_name='投票情况')  # 不是实际的字段

    created_at = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True,verbose_name='更新时间')

    class Meta:
        verbose_name = '回答'
        verbose_name_plural = verbose_name
        ordering = ('-is_answer','-created_at',)

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        '''得票数'''
        dic = Counter(self.votes.values_list('value',flat=True)) #赞同数多少，反对数多少
        return dic[True] - dic[False]

    def get_downvoters(self):
        '''反对的用户'''
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_accecpted_answer(self):
        return Answer.objects.get(question=self,is_answer = True)

    def accept_answer(self):
        #当一个问题有多个回答的时候，只能采纳一个回答，其他回答一律设置为未接受
        answer_set = Answer.objects.filter(question=self.question)#查询当前问题的所有回答
        answer_set.update(is_answer=False) #一律置为未接受


        self.is_answer = True
        self.save()
        self.question.has_answer=True
        self.question.save()

