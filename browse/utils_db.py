from collections import namedtuple, defaultdict

from django.db import connection


def namedtuplefetchall(query, param_list):
	"""Return all rows from a cursor as a namedtuple"""
	with connection.cursor() as cursor:
		cursor.execute(query, param_list)
		desc = cursor.description
		nt_result = namedtuple('Result', [col[0] for col in desc])
		return [nt_result(*row) for row in cursor.fetchall()]


def get_rating_count_package(pkg_id):
	""":returns an array with index as rating-value and value as count"""
	results = namedtuplefetchall(
		'select rating, count(distinct user_id)\
		from browse_packagerating\
		where package_id = %s\
		group by rating', [pkg_id])
	ratings = [0, 0, 0, 0, 0, 0]
	for i in results:
		ratings[i.rating] = i.count
	return ratings

def get_rating_package(pkg_id):
	""":returns average rating of package"""
	results = namedtuplefetchall(
		'select avg(rating) as avg_rating\
		from browse_packagerating\
		where package_id = %s', [pkg_id])
	return results[0].avg_rating


def get_reviews_package(user_id, pkg_id):
	"""returns list of comments as tuple (package_id, user_id, rating, comment, time, nlikes, ndislikes)"""
	results = namedtuplefetchall('select comment.package_id,\
		comment.user_id,\
		rate.rating,\
		comment.comment,\
		comment.time,\
		(select count(liked.user_id)\
		from browse_packagecommentreact liked\
		where liked.post_id = comment.id\
			and liked.liked = true)		 as nlikes,\
		(select count(disliked.user_id)\
		from browse_packagecommentreact disliked\
		where disliked.post_id = comment.id\
			and disliked.disliked = true) as ndislikes\
	from browse_packagecomment comment\
				left join browse_packagerating rate on rate.package_id = comment.package_id and\
													rate.user_id = comment.user_id\
	where comment.user_id = %s and comment.package_id = %s\
	UNION\
	DISTINCT\
	select comment.package_id,\
			comment.user_id,\
			rate.rating,\
			comment.comment,\
			comment.time,\
			(select count(liked.user_id)\
			from browse_packagecommentreact liked\
			where liked.post_id = comment.id\
				and liked.liked = true)		 as nlikes,\
			(select count(disliked.user_id)\
			from browse_packagecommentreact disliked\
			where disliked.post_id = comment.id\
				and disliked.disliked = true) as ndislikes\
	from browse_packagecomment comment\
				left join browse_packagerating rate on rate.package_id = comment.package_id and\
													rate.user_id = comment.user_id\
	where comment.user_id != %s and comment.package_id = %s\
	order by time desc', [user_id, pkg_id, user_id, pkg_id])
	return results


def get_react_count_package(post):
	""":returns (likes_count, dislikes_count) of post in package"""
	from browse.models import PackageCommentReact
	nliked = PackageCommentReact.objects.filter(post=post, liked=True).count()
	ndisliked = PackageCommentReact.objects.filter(post=post, disliked=True).count()
	return nliked, ndisliked


def get_rating_restaurant(rest_id):
	""":returns avg rating over all users from all branches"""
	results = namedtuplefetchall(
		'select avg(rating) as avg_rating\
		from browse_branchrating join accounts_restaurantbranch\
									on browse_branchrating.branch_id = accounts_restaurantbranch.id\
		where accounts_restaurantbranch.restaurant_id = %s', [rest_id])
	return results[0].avg_rating


def get_rating_branch(branch_id):
	""":returns avg rating over all users branch"""
	results = namedtuplefetchall(
		'select avg(rating) as avg_rating\
		from browse_branchrating join accounts_restaurantbranch\
									on browse_branchrating.branch_id = accounts_restaurantbranch.id\
		where accounts_restaurantbranch.restaurant_id = %s', [branch_id])
	return results[0].avg_rating


def get_reviews_branch(user_id, branch_id):
	"""returns list of comments as tuple (branch_id, user_id, rating, comment, time, nlikes, ndislikes)"""
	results = namedtuplefetchall('select comment.branch_id,\
		comment.user_id,\
		rate.rating,\
		comment.comment,\
		comment.time,\
		(select count(liked.user_id)\
		from browse_branchcommentreact liked\
		where liked.post_id = comment.id\
			and liked.liked = true)       as nlikes,\
		(select count(disliked.user_id)\
		from browse_branchcommentreact disliked\
		where disliked.post_id = comment.id\
			and disliked.disliked = true) as ndislikes\
	from browse_branchcomment comment\
		left join browse_branchrating rate on rate.branch_id = comment.branch_id and\
												rate.user_id = comment.user_id\
	where comment.user_id = %s\
		and comment.branch_id = %s\
	UNION\
	DISTINCT\
	select comment.branch_id,\
			comment.user_id,\
			rate.rating,\
			comment.comment,\
			comment.time,\
			(select count(liked.user_id)\
			from browse_branchcommentreact liked\
			where liked.post_id = comment.id\
				and liked.liked = true)       as nlikes,\
			(select count(disliked.user_id)\
			from browse_branchcommentreact disliked\
			where disliked.post_id = comment.id\
				and disliked.disliked = true) as ndislikes\
	from browse_branchcomment comment\
			left join browse_branchrating rate on rate.branch_id = comment.branch_id and\
													rate.user_id = comment.user_id\
	where comment.user_id != %s\
		and comment.branch_id = %s\
	order by time desc', [user_id, branch_id, user_id, branch_id])
	return results


def get_react_count_branch(post):
	""":returns (likes_count, dislikes_count) of post in branch"""
	from browse.models import BranchCommentReact
	nliked = BranchCommentReact.objects.filter(post=post, liked=True).count()
	ndisliked = BranchCommentReact.objects.filter(post=post, disliked=True).count()
	return nliked, ndisliked


def post_rating_package(user, pkg_id, rating):
	""" create or update user rating on package """
	from browse.models import PackageRating
	from browse.models import Package
	package = Package.objects.exclude(user=user).get(id=pkg_id)
	if PackageRating.objects.exists(package=package, user=user):
		post = PackageRating.objects.get(package=package, user=user)
		post.rating = rating
		post.save()
	else:
		PackageRating(rating=rating, package=package, user=user).save()


def post_comment_package(user, pkg_id, comment):
	""" create or update user comment on package """
	from browse.models import PackageComment
	from browse.models import Package
	package = Package.objects.exclude(user=user).get(id=pkg_id)
	if PackageComment.objects.exists(package=package, user=user):
		post = PackageComment.objects.get(package=package, user=user)
		post.comment = comment
		post.save()
	else:
		PackageComment(comment=comment, package=package, user=user).save()


def post_comment_react_package(user, comment_id, react):
	""" create or update react on existing post of any user on package """
	from browse.models import PackageCommentReact
	post = PackageCommentReact.objects.get(id=comment_id)
	like = (react == 'like')
	dislike = (react == 'dislike')
	if PackageCommentReact.objects.exists(post=post, user=user):
		react = PackageCommentReact.objects.get(post=post, user=user)
	else:
		react = PackageCommentReact(post=post, user=user)
	if like:
		react.liked = like
	if dislike:
		react.disliked = dislike
	react.save()


def post_rating_branch(user, branch_id, rating):
	""" create or update user rating on branch """
	from browse.models import BranchRating
	from accounts.models import RestaurantBranch
	branch = RestaurantBranch.objects.exclude(user=user).get(id=branch_id)
	if BranchRating.objects.exists(branch=branch, user=user):
		post = BranchRating.objects.get(branch=branch, user=user)
		post.rating = rating
		post.save()
	else:
		BranchRating(rating=rating, branch=branch, user=user).save()


def post_comment_branch(user, branch_id, comment):
	""" create or update user comment on branch """
	from browse.models import BranchComment
	from accounts.models import RestaurantBranch
	branch = RestaurantBranch.objects.exclude(user=user).get(id=branch_id)
	if BranchComment.objects.exists(branch=branch, user=user):
		post = BranchComment.objects.get(branch=branch, user=user)
		post.comment = comment
		post.save()
	else:
		BranchComment(comment=comment, branch=branch, user=user).save()


def post_comment_react_branch(user, comment_id, react):
	""" create or update react on existing post of any user on branch """
	from browse.models import BranchCommentReact
	post = BranchCommentReact.objects.get(id=comment_id)
	like = (react == 'like')
	dislike = (react == 'dislike')
	if BranchCommentReact.objects.exists(post=post, user=user):
		react = BranchCommentReact.objects.get(post=post, user=user)
	else:
		react = BranchCommentReact(post=post, user=user)
	if like:
		react.liked = like
	if dislike:
		react.disliked = dislike
	react.save()
