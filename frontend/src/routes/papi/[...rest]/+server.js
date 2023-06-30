export async function DELETE({locals, params}) {
	await locals.api.delete(params.rest, locals.user.token)
	return new Response()
}
