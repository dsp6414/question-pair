import numpy as np
import tensorflow as tf
import numpy as np
import json
import datetime

maxSeqLength = 30
number_of_examples_to_take = 100000
global_pair_counter = 0


def load_matrices():
	q1_ids = np.load('q1_ids_matrix.npy')
	q2_ids = np.load('q2_ids_matrix.npy')

def load_data_saved():
	with open('stemmed_split_sentences','r') as myfile:
		data = json.load(myfile)
	return data

def load_question_pair():
	global global_pair_counter
	question_one_matrice = np.load('q1_ids_matrix.npy')
	question_two_matrice = np.load('q2_ids_matrix.npy')
	is_same_matrice = np.load('is_same_matrix.npy')
	if np.sum(question_one_matrice[global_pair_counter]) == 0 or np.sum(question_one_matrice[global_pair_counter])==0:
		global_pair_counter+=1
		error = 1
		question_one = question_one_matrice
		question_two = question_two_matrice
		is_same = is_same_matrice
		return question_one, question_two, is_same, error
	else:
		try:
			zero_index = question_one_matrice[global_pair_counter].tolist().index(0)
			question_one = np.roll(question_one_matrice[global_pair_counter],30-zero_index)
		except ValueError:
			question_one = question_one_matrice[global_pair_counter]

		try:
			zero_index = question_two_matrice[global_pair_counter].tolist().index(0)
			question_two = np.roll(question_two_matrice[global_pair_counter],30-zero_index)
		except ValueError:
			question_two = question_two_matrice[global_pair_counter]
		is_same = is_same_matrice[global_pair_counter]
		global_pair_counter+=1
		#print global_pair_counter
		error = 0
		#question_one = 
		question_one = question_one.reshape(question_one.shape[0],-1).T
		question_two = question_two.reshape(question_two.shape[0],-1).T
		question_one[question_one==3999999] = 214476 
		question_two[question_two==3999999] = 214476
		return question_one,question_two,is_same,error



#load_matrices()

wordVectors = np.load('word_vectors.npy')
print wordVectors.shape
batchSize = 1
lstmUnits = 64
numClasses = 30
iterations = 100000
numDimensions = 300
learning_rate = 0.0001
tf.reset_default_graph()
keep_prob = 0.75
graph = tf.Graph()
lstm_layers = 3
with graph.as_default():
	'''
	label = tf.placeholder(tf.int32, [1], name='label')
	with tf.variable_scope('Inference',reuse=False):
		input_data_q1 = tf.placeholder(tf.int32, [batchSize, maxSeqLength])
		data_q1 = tf.Variable(tf.zeros([batchSize, maxSeqLength, numDimensions]),dtype=tf.float32)
		data_q1 = tf.nn.embedding_lookup(wordVectors,input_data_q1)
		data_q1 = tf.cast(data_q1,tf.float32)
		#weights_q1 = tf.Variable(tf.truncated_normal([lstmUnits, numClasses]))
		#bias_q1 = tf.Variable(tf.constant(0.1, shape=[numClasses]))	
		weights_q1 = tf.get_variable('weights_q1',[lstmUnits, numClasses],initializer=tf.contrib.layers.xavier_initializer())
		initialized = tf.constant(0.1, shape=[numClasses])
		bias_q1 = tf.get_variable('bias_q1',initializer=initialized)
		lstmCell_1 = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
		lstmCell_1 = tf.contrib.rnn.DropoutWrapper(cell=lstmCell_1, output_keep_prob=0.75)
		value_1, _ = tf.nn.dynamic_rnn(lstmCell_1, data_q1, dtype=tf.float32)
		last_1 = tf.gather(value_1, int(value_1.get_shape()[0]) - 1)
		prediction_1 = (tf.matmul(last_1, weights_q1) + bias_q1)
			
	#scope.reuse_variables()
	with tf.variable_scope('Inference',reuse=True):
		input_data_q2 = tf.placeholder(tf.int32, [batchSize, maxSeqLength])
		data_q2 = tf.Variable(tf.zeros([batchSize, maxSeqLength, numDimensions]),dtype=tf.float32)
		data_q2 = tf.nn.embedding_lookup(wordVectors,input_data_q2)
		data_q2 = tf.cast(data_q2,tf.float32)
		weights_q2 = tf.get_variable('weights_q1',shape=[lstmUnits, numClasses])
		bias_q2 = tf.get_variable('bias_q1',shape=[numClasses])	
		lstmCell_2 = tf.contrib.rnn.BasicLSTMCell(lstmUnits,reuse=tf.get_variable_scope().reuse)
		lstmCell_2 = tf.contrib.rnn.DropoutWrapper(cell=lstmCell_2, output_keep_prob=0.75)
		value_2, _ = tf.nn.dynamic_rnn(lstmCell_2, data_q2, dtype=tf.float32)
		last_2 = tf.gather(value_2, int(value_2.get_shape()[0]) - 1)
		prediction_2 = (tf.matmul(last_2, weights_q2) + bias_q2)
	
	'''
	#GRAPH ATTEMPT 2 : 

	label = tf.placeholder(tf.int32, [1], name='label')
	with tf.variable_scope('Inference',reuse=False):
		input_data_q1 = tf.placeholder(tf.int32, [batchSize, maxSeqLength])
		#data_q1 = tf.Variable(tf.zeros([batchSize, maxSeqLength, numDimensions]),dtype=tf.float32)
		cells=[]
		data_q1 = tf.nn.embedding_lookup(wordVectors,input_data_q1)
		data_q1 = tf.cast(data_q1,tf.float32)
		lstmCell_1 = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
		for _ in range(lstmUnits):
			question1_drop = tf.contrib.rnn.DropoutWrapper(lstmCell_1, output_keep_prob=keep_prob)
			cells.append(question1_drop)
		question1_multi_lstm = tf.contrib.rnn.MultiRNNCell(cells)
		#question1_multi_lstm = tf.contrib.rnn.MultiRNNCell([question1_drop for _ in range(lstm_layers)])
		q1_initial_state = question1_multi_lstm.zero_state(batchSize, tf.float32)
		question1_outputs, question1_final_state = tf.nn.dynamic_rnn(question1_multi_lstm, data_q1, initial_state=q1_initial_state)
			
	#scope.reuse_variables()
	with tf.variable_scope('Inference',reuse=True) as scope:
		scope.reuse_variables()
		input_data_q2 = tf.placeholder(tf.int32, [batchSize, maxSeqLength])
		#data_q2 = tf.Variable(tf.zeros([batchSize, maxSeqLength, numDimensions]),dtype=tf.float32)
		data_q2 = tf.nn.embedding_lookup(wordVectors,input_data_q2)
		data_q2 = tf.cast(data_q2,tf.float32)
		lstmCell_2 = tf.contrib.rnn.BasicLSTMCell(lstmUnits)
		cells = []
		for _ in range(lstmUnits):
			question2_drop = tf.contrib.rnn.DropoutWrapper(lstmCell_2, output_keep_prob=keep_prob)
			cells.append(question2_drop)
		#question2_drop = tf.contrib.rnn.DropoutWrapper(lstmCell_2, output_keep_prob=keep_prob)
		question2_multi_lstm = tf.contrib.rnn.MultiRNNCell(cells)
		q2_initial_state = question2_multi_lstm.zero_state(batchSize, tf.float32)
		question2_outputs, question2_final_state = tf.nn.dynamic_rnn(question2_multi_lstm, data_q2, initial_state=q2_initial_state)


	#LOSS ATTEMPT 4
	'''
	print 'Q1  OP SHAPE== ' + str(question1_outputs.get_shape)
	diff = tf.sqrt(tf.reduce_sum(tf.square(tf.subtract(question1_outputs[:, -1, :], question2_outputs[:, -1, :])), reduction_indices=1))

	margin = tf.constant(1.) 
	labels = tf.to_float(label)
	match_loss = tf.expand_dims(tf.square(diff, 'match_term'), 0)
	mismatch_loss = tf.expand_dims(tf.maximum(0., tf.subtract(margin, tf.square(diff)), 'mismatch_term'), 0)

	loss = tf.add(tf.matmul(tf.expand_dims(labels,1), match_loss), tf.matmul(tf.expand_dims((1 - labels),1), mismatch_loss), 'loss_add')
	final_loss = tf.reduce_mean(loss)
	'''
	# LOSS FUNCTION ATTEMPT 3
	'''
	diff = tf.sqrt(tf.reduce_sum(tf.square(tf.subtract(question1_outputs, question2_outputs)), reduction_indices=1, keep_dims=True))
	margin = tf.constant(1.0) 
	labels = tf.to_float(label)
	match_loss = tf.expand_dims(tf.square(diff, 'match_term'), 0)
	mismatch_loss = tf.expand_dims(tf.maximum(0., tf.subtract(margin, tf.square(diff)), 'mismatch_term'), 0)
	loss = tf.add(tf.matmul(labels, match_loss), tf.matmul((1 - labels), mismatch_loss), 'loss_add')
	final_loss = tf.reduce_mean(loss)
	'''
	
	#LOSS FUNCTION ATTEMPT 2
	d = tf.reduce_sum(tf.square(question1_outputs-question2_outputs), 1)
	label = tf.to_float(label)
	margin = tf.constant(1.0)
	d_sqrt = tf.sqrt(d)
	loss = label * tf.square(tf.maximum(0., margin - d_sqrt)) + (1 - label) * d
	final_loss = 0.5 * tf.reduce_mean(loss)
	
	
	
	
	# LOSS FUNCTION ATTEMPT 1
	'''
	d = tf.reduce_sum(tf.square(prediction_1-prediction_2), 1, keep_dims=True)
	label = tf.to_float(label)
	margin = 0.2
	d_sqrt = tf.sqrt(d)
	loss = label * tf.square(tf.maximum(0., margin - d_sqrt)) + (1 - label) * d
	loss = 0.5 * tf.reduce_mean(loss)
	'''
#	logdir = "tensorboard/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "/"
#	tf.summary.scalar('Loss', loss)
#	merged = tf.summary.merge_all()
#	writer = tf.summary.FileWriter(logdir, sess.graph)
	
	optimizer = tf.train.AdamOptimizer(learning_rate).minimize(final_loss)
	sess = tf.InteractiveSession()
	
	logdir = "tensorboard/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "/"
	loss_summary = tf.summary.scalar('Loss', final_loss)
	merged = tf.summary.merge_all()
	writer = tf.summary.FileWriter(logdir, sess.graph)
	
	saver = tf.train.Saver(max_to_keep=1)
	sess.run(tf.global_variables_initializer())
	
	
	for iteration_number in xrange(0,100000):
		question_one,question_two,is_same, error = load_question_pair()
		if error:
			pass
		else:
			print iteration_number
			loss_obtained = sess.run([final_loss], {input_data_q1: question_one, input_data_q2:question_two,label:is_same})
			if iteration_number%50==0:
				print 'LOSS AT STEP ' + str(iteration_number) + ' IS == ' +str(loss_obtained)
			
			if iteration_number%50 == 0 and iteration_number !=0:
				summary = sess.run(loss_summary, {input_data_q1: question_one, input_data_q2:question_two,label:is_same})
				writer.add_summary(summary, iteration_number)
			if iteration_number%20000 == 0 and iteration_number !=0:
				save_path = saver.save(sess, "models/siamese.ckpt", global_step=iteration_number)
				print("saved to %s" % save_path)

	writer.close()


'''
for i in xrange(0,100000):
	question_one,question_two,is_same,error = load_question_pair()
	question_one = question_one.reshape(question_one.shape[0],-1).T
	print question_one
	question_one[question_one==3999999] = 214476 
	print question_one
	print is_same.shape
	#print error
'''